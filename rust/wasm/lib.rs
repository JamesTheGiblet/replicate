//! Replicant WASM entry point

use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn greet() -> String {
    "🧬 Replicant WASM is running!".to_string()
}
