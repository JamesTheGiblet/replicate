//! Environment module - dynamic world with resources, threats, seasons

use rand::Rng;
use rand::SeedableRng;
use serde::{Deserialize, Serialize};
/// Resource patch in the environment
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResourcePatch {
    pub x: f32,
    pub y: f32,
    pub energy: f32,
    pub max_energy: f32,
    pub regeneration_rate: f32,
    pub depleted: bool,
    pub depletion_tick: u32,
}

impl ResourcePatch {
    pub fn new(x: f32, y: f32, max_energy: f32, regeneration_rate: f32) -> Self {
        let mut rng = rand::thread_rng();
        Self {
            x,
            y,
            energy: max_energy * rng.gen_range(0.5..1.0),
            max_energy,
            regeneration_rate,
            depleted: false,
            depletion_tick: 0,
        }
    }

    pub fn regenerate(&mut self, tick: u32, season_factor: f32) {
        if self.depleted {
            if tick - self.depletion_tick > 20 {
                self.depleted = false;
                self.energy = self.max_energy * 0.1;
            }
            return;
        }
        let regen = self.regeneration_rate * season_factor;
        self.energy = (self.energy + regen).min(self.max_energy);
    }

    pub fn harvest(&mut self, amount: f32) -> f32 {
        let take = amount.min(self.energy * 0.5);
        self.energy -= take;
        if self.energy < 1.0 {
            self.depleted = true;
        }
        take
    }
}

/// Threat zone in the environment
#[derive(Debug, Clone)]
pub struct ThreatZone {
    pub x: f32,
    pub y: f32,
    pub radius: f32,
    pub intensity: f32,
    pub active: bool,
    pub tick_created: u32,
    pub tick_decay: u32,
}

/// Environment metrics
#[derive(Debug, Clone)]
pub struct EnvironmentMetrics {
    pub population_stability: f32,
    pub energy_stability: f32,
    pub threat_response: f32,
    pub resource_utilization: f32,
    pub overall_health: f32,
}

impl Default for EnvironmentMetrics {
    fn default() -> Self {
        Self {
            population_stability: 0.5,
            energy_stability: 0.5,
            threat_response: 0.5,
            resource_utilization: 0.5,
            overall_health: 0.5,
        }
    }
}

/// The environment - resources, threats, seasons
#[derive(Debug, Clone)]
pub struct Environment {
    pub width: f32,
    pub height: f32,
    pub tick: u32,
    pub patches: Vec<ResourcePatch>,
    pub threats: Vec<ThreatZone>,
    pub season_cycle: u32,
    pub season_phase: u32,
    pub carrying_capacity: u32,
    pub metrics: EnvironmentMetrics,
    pub population_history: Vec<u32>,
    pub energy_history: Vec<f32>,
    /// A history of ticks when new patches were discovered.
    pub discovery_history: Vec<u32>,
}

impl Environment {
    pub fn new(width: f32, height: f32, n_patches: usize, seed: u64) -> Self {
        let mut rng = rand::rngs::StdRng::seed_from_u64(seed);
        
        let mut patches = Vec::new();
        for _ in 0..n_patches {
            let x = rng.gen_range(5.0..width - 5.0);
            let y = rng.gen_range(5.0..height - 5.0);
            let max_energy = rng.gen_range(80.0..120.0);
            let regeneration_rate = rng.gen_range(0.5..1.5);
            patches.push(ResourcePatch::new(x, y, max_energy, regeneration_rate));
        }

        Self {
            width,
            height,
            tick: 0,
            patches,
            threats: Vec::new(),
            season_cycle: 50,
            season_phase: 0,
            carrying_capacity: 20,
            metrics: EnvironmentMetrics::default(),
            population_history: Vec::new(),
            energy_history: Vec::new(),
            discovery_history: Vec::new(),
        }
    }

    pub fn season_factor(&self) -> f32 {
        let phase = self.season_phase as f32 / self.season_cycle as f32;
        1.0 + 0.5 * (phase * 2.0 * std::f32::consts::PI).sin()
    }

    pub fn get_resource_at(&self, x: f32, y: f32, radius: f32) -> f32 {
        let mut total = 0.0;
        for patch in &self.patches {
            let dist = ((patch.x - x).powi(2) + (patch.y - y).powi(2)).sqrt();
            if dist < radius && !patch.depleted {
                total += patch.energy * (1.0 - dist / radius);
            }
        }
        total
    }

    /// Direction (normalized) and distance toward the nearest non-depleted patch.
    /// Used so agents can walk to a patch instead of foraging in place with nothing nearby.
    pub fn nearest_patch_info(&self, x: f32, y: f32) -> Option<(f32, f32, f32)> {
        self.patches
            .iter()
            .filter(|p| !p.depleted)
            .map(|p| {
                let dx = p.x - x;
                let dy = p.y - y;
                (dx, dy, (dx * dx + dy * dy).sqrt())
            })
            .min_by(|a, b| a.2.partial_cmp(&b.2).unwrap())
            .map(|(dx, dy, dist)| {
                if dist < 0.001 {
                    (0.0, 0.0, dist)
                } else {
                    (dx / dist, dy / dist, dist)
                }
            })
    }

    pub fn harvest_resource(&mut self, x: f32, y: f32, amount: f32) -> f32 {
        let mut harvested = 0.0;
        for patch in &mut self.patches {
            let dist = ((patch.x - x).powi(2) + (patch.y - y).powi(2)).sqrt();
            if dist < 3.0 && !patch.depleted {
                let take = (amount - harvested).min(patch.energy * 0.5);
                if take > 0.0 {
                    patch.energy -= take;
                    harvested += take;
                    if patch.energy < 1.0 {
                        patch.depleted = true;
                        patch.depletion_tick = self.tick;
                    }
                }
                if harvested >= amount {
                    break;
                }
            }
        }
        harvested
    }

    /// Direction (normalized) toward the richest known, non-depleted patch - used for migration.
    pub fn richest_patch_direction(&self, x: f32, y: f32) -> Option<(f32, f32)> {
        self.patches
            .iter()
            .filter(|p| !p.depleted && p.energy > 10.0)
            .max_by(|a, b| a.energy.partial_cmp(&b.energy).unwrap())
            .map(|p| {
                let dx = p.x - x;
                let dy = p.y - y;
                let dist = (dx * dx + dy * dy).sqrt().max(0.001);
                (dx / dist, dy / dist)
            })
    }

    /// Attempt to discover a brand new resource patch in unexplored territory near (x, y).
    /// Fails if a patch already exists nearby, since that area is already known.
    pub fn try_discover_patch(&mut self, x: f32, y: f32, rng: &mut impl Rng) -> bool {
        let already_known = self.patches.iter().any(|p| {
            let dist = ((p.x - x).powi(2) + (p.y - y).powi(2)).sqrt();
            dist < 8.0
        });
        if already_known {
            return false;
        }
        let px = (x + rng.gen_range(-3.0..3.0)).clamp(2.0, self.width - 2.0);
        let py = (y + rng.gen_range(-3.0..3.0)).clamp(2.0, self.height - 2.0);
        let max_energy = rng.gen_range(80.0..120.0);
        let regeneration_rate = rng.gen_range(0.5..1.5);
        self.patches.push(ResourcePatch::new(px, py, max_energy, regeneration_rate));
        self.discovery_history.push(self.tick);
        true
    }

    /// Terraform a new, smaller resource patch at (x, y) - used by the Builder role.
    pub fn spawn_patch_near(&mut self, x: f32, y: f32, rng: &mut impl Rng) {
        let px = (x + rng.gen_range(-1.5..1.5)).clamp(2.0, self.width - 2.0);
        let py = (y + rng.gen_range(-1.5..1.5)).clamp(2.0, self.height - 2.0);
        self.patches.push(ResourcePatch::new(px, py, 60.0, 1.2));
    }

    pub fn detect_threat(&self, x: f32, y: f32) -> (bool, f32) {
        for threat in &self.threats {
            if threat.active {
                let dist = ((threat.x - x).powi(2) + (threat.y - y).powi(2)).sqrt();
                if dist < threat.radius {
                    return (true, threat.intensity * (1.0 - dist / threat.radius));
                }
            }
        }
        (false, 0.0)
    }

    pub fn update(&mut self, population: u32, avg_energy: f32, agents_in_threat: u32) {
        self.tick += 1;
        self.season_phase = (self.season_phase + 1) % self.season_cycle;

        // Update metrics history
        self.population_history.push(population);
        if self.population_history.len() > 100 {
            self.population_history.remove(0);
        }
        self.energy_history.push(avg_energy);
        if self.energy_history.len() > 100 {
            self.energy_history.remove(0);
        }
        // Prune discovery history to the last 1000 ticks
        self.discovery_history.retain(|&t| self.tick - t < 1000);


        // Recalculate health metrics
        let pop_f = population as f32;
        let capacity_f = self.carrying_capacity as f32;
        let pop_stability = (1.0 - (pop_f - capacity_f).abs() / capacity_f).clamp(0.0, 1.0);

        let energy_stability = (avg_energy / 100.0).clamp(0.0, 1.0);

        let total_possible_energy: f32 = self.patches.iter().map(|p| p.max_energy).sum();
        let current_resource_energy: f32 = self.patches.iter().map(|p| p.energy).sum();
        let resource_utilization = if total_possible_energy > 0.0 {
            (current_resource_energy / total_possible_energy).clamp(0.0, 1.0)
        } else {
            0.5
        };

        let threat_response = if self.threats.is_empty() {
            1.0 // Perfect response if there are no threats
        } else if population > 0 {
            // The proportion of the population that is NOT in a threat zone
            (1.0 - (agents_in_threat as f32 / population as f32)).clamp(0.0, 1.0)
        } else {
            1.0 // No agents to be threatened
        };

        self.metrics.population_stability = pop_stability;
        self.metrics.energy_stability = energy_stability;
        self.metrics.resource_utilization = resource_utilization;
        self.metrics.threat_response = threat_response;
        self.metrics.overall_health = (pop_stability * 0.3) + (energy_stability * 0.3) + (resource_utilization * 0.2) + (threat_response * 0.2);

        let season_factor = self.season_factor();

        for patch in &mut self.patches {
            patch.regenerate(self.tick, season_factor);
        }

        let base_chance = 0.02 / (season_factor + 0.5);
        let mut rng = rand::thread_rng();
        if rng.gen_bool(base_chance as f64) && self.threats.len() < 3 {
            let x = rng.gen_range(10.0..self.width - 10.0);
            let y = rng.gen_range(10.0..self.height - 10.0);
            let radius = rng.gen_range(3.0..8.0);
            let intensity = rng.gen_range(0.3..0.8);
            self.threats.push(ThreatZone {
                x,
                y,
                radius,
                intensity,
                active: true,
                tick_created: self.tick,
                tick_decay: self.tick + rng.gen_range(10..30),
            });
        }

        for threat in &mut self.threats {
            if self.tick > threat.tick_decay {
                threat.active = false;
            }
        }
        self.threats.retain(|t| t.active);
    }

    pub fn is_stable(&self, threshold: f32) -> bool {
        self.metrics.overall_health > threshold
    }

    pub fn get_health_report(&self) -> String {
        let total_energy: f32 = self.patches.iter().map(|p| p.energy).sum();
        format!(
            "🌿 Health: {:.2} | Season: {} | Patches: {} | Threats: {} | Energy: {:.1}",
            self.metrics.overall_health,
            if self.season_factor() > 1.0 { "Rich" } else { "Poor" },
            self.patches.len(),
            self.threats.len(),
            total_energy
        )
    }
}
