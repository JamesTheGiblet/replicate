//! Replicant - Hybrid bio-inspired swarm framework
//!
//! Born pregnant. Born ready. Born signed.
//! The swarm learns. The liar pays.

#![cfg_attr(not(feature = "std"), no_std)]

pub mod core;
pub mod agent;
pub mod world;
pub mod environment;
pub mod adversary;
pub mod viz;
pub mod founders;
pub mod awareness;

// WASM module (only included when targeting wasm)
#[cfg(target_arch = "wasm32")]
pub mod wasm;

// Re-exports
pub use core::*;
pub use agent::*;
pub use world::*;
pub use environment::*;
pub use adversary::*;
pub use viz::*;
pub use founders::*;
pub use awareness::*;
