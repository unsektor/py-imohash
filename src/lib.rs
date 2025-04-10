use std::fs;
use imohash::Hasher;

use pyo3::prelude::*;
use pyo3::Python;
use pyo3::exceptions::PyFileNotFoundError;
use pyo3::types::PyBytes;

// hardcode, as `imohash::{SAMPLE_THRESHOLD, SAMPLE_SIZE}` constants are private
const SAMPLE_THRESHOLD: u32 = 128 * 1024;
const SAMPLE_SIZE: u32 = 16 * 1024;

#[pyclass]
#[derive(Debug, Clone)]
pub struct Imohash {
    instance: Hasher,
    // Workaround to create correct representation, as these settings are private in Hasher instance
    sample_size: u32,
    sample_threshold: u32,
}

#[pyclass]
#[derive(Debug, Clone)]
pub struct Hash {
    value: u128
}

#[pymethods]
impl Hash {
    #[new]
    #[pyo3(signature = (value))]
    fn new(value: u128) -> Self {
        Hash {
            value: value
        }
    }

    fn digest(&self, py: Python) -> PyObject {
        let slice = self.value.to_le_bytes().to_vec();
        PyBytes::new(py, &slice).into()
    }

    fn hexdigest(&self) -> String {
        hex::encode(self.value.to_le_bytes())
    }

    fn __int__(&self) -> u128 {
        self.value
    }

    fn __bytes__(&self, py: Python) -> PyObject {
        self.digest(py)
    }

    fn __str__(&self) -> String {
        self.hexdigest()
    }

    fn __repr__(&self) -> String {
        format!("Hash(value={value:?})", value = self.value)
    }
}

#[pymethods]
impl Imohash {
    #[new]
    #[pyo3(signature = (sample_threshold=None, sample_size=None))]
    fn new(sample_threshold: Option<u32>, sample_size: Option<u32>) -> PyResult<Self> {
        let sample_threshold = sample_threshold.unwrap_or(SAMPLE_THRESHOLD);
        let sample_size = sample_size.unwrap_or(SAMPLE_SIZE);

        Ok(Imohash {
            instance: Hasher::with_sample_size_and_threshold(sample_size, sample_threshold),
            sample_size: sample_size,
            sample_threshold: sample_threshold,
        })
    }

    #[pyo3(signature = (data=None))]
    fn get(&self, py: Python<'_>, data: Option<&[u8]>) -> PyResult<Hash> {
        py.allow_threads(|| {
            return Ok(Hash { value: self.instance.sum(data.unwrap()).unwrap() });
        })
    }

    #[pyo3(signature = (path=None))]
    fn get_for_file(&self, py: Python<'_>, path: Option<&str>) -> PyResult<Hash> {
        // protect from endless "file", e.g. `/dev/random`
        let metadata = fs::metadata(path.unwrap())?;
        if !metadata.is_file() || metadata.file_type().is_symlink() {
            return Err(PyFileNotFoundError::new_err(format!("Path is not a file: {path:?}", path = path.unwrap())));
        }

        py.allow_threads(|| {
            return Ok(Hash { value: self.instance.sum_file(path.unwrap()).unwrap() });
        })
    }

    fn __repr__(&self) -> String {
        format!(
            "Imohash(sample_size={sample_size:?}, sample_threshold={sample_threshold:?})",
            sample_size = self.sample_size,
            sample_threshold = self.sample_threshold,
        )
    }
}

#[pymodule]
#[pyo3(name = "imohash_rs")]
fn init(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add("SAMPLE_THRESHOLD", SAMPLE_THRESHOLD)?;
    m.add("SAMPLE_SIZE", SAMPLE_SIZE)?;
    m.add_class::<Imohash>()?;
    m.add_class::<Hash>()?;
    Ok(())
}
