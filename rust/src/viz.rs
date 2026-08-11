//! Visualization module (placeholder for future WASM/terminal viz)

use crate::world::World;

pub struct Viz {
    pub width: u32,
    pub height: u32,
}

impl Viz {
    pub fn new(width: u32, height: u32) -> Self {
        Self { width, height }
    }

    pub fn render(&self, _world: &World, _tick: u32) {
        // Placeholder - will be implemented with terminal or WASM rendering
        println!("🧬 Replicant Visualization (placeholder)");
    }
}
