//! Replicant WASM - Browser visualization bindings

use serde_json::to_string_pretty;
use wasm_bindgen::prelude::*;
use web_sys::{CanvasRenderingContext2d, HtmlCanvasElement};

use replicant::founders::create_founders;
use replicant::*;

/// WebAssembly bindings for Replicant
#[wasm_bindgen]
pub struct ReplicantWASM {
    world: World,
    canvas: HtmlCanvasElement,
    ctx: CanvasRenderingContext2d,
}

#[wasm_bindgen]
impl ReplicantWASM {
    #[wasm_bindgen(constructor)]
    pub fn new(canvas_id: &str) -> Result<ReplicantWASM, JsValue> {
        let window = web_sys::window().expect("no window");
        let document = window.document().expect("no document");
        
        let canvas = document
            .get_element_by_id(canvas_id)
            .expect("canvas not found")
            .dyn_into::<HtmlCanvasElement>()?;
        
        let ctx = canvas
            .get_context("2d")?
            .unwrap()
            .dyn_into::<CanvasRenderingContext2d>()?;
        
        // Initialize the world
        let config = WorldConfig {
            seed: 42,
            ticks: 1000,
            commit_attestations: 2,
            n_patches: 10,
        };
        let world = World::new(config);
        
        let mut wasm_app = ReplicantWASM {
            world,
            canvas,
            ctx,
        };

        for (_name, agent) in create_founders() {
            wasm_app.world.agents.insert(agent.scp_id.clone(), agent);
        }
        
        Ok(wasm_app)
    }
    
    pub fn start(&mut self) -> Result<(), JsValue> {
        // This will be used for a proper animation loop later
        Ok(())
    }
    
    pub fn pause(&mut self) {
        // Placeholder for pause functionality
    }
    
    pub fn step(&mut self) -> Result<(), JsValue> {
        // The core logic update. Instead of just incrementing the tick,
        // we now run the full sense-decide-resolve loop. This is what
        // enables agent movement, claim creation, and other behaviors.
        self.world.tick();
        // The render call was already here, but now it will draw the
        // updated agent positions and world state from the tick() execution.
        // self.render()?; // render() is called from JS side now for better control.
        Ok(())
    }
    
    pub fn render(&self) -> Result<(), JsValue> {
        let width = self.canvas.width() as f64;
        let height = self.canvas.height() as f64;
        
        self.ctx.clear_rect(0.0, 0.0, width, height);

        // Draw background
        self.ctx.set_fill_style_str("#0B0E14");
        self.ctx.fill_rect(0.0, 0.0, width, height);
        
        // Draw resources
        for patch in &self.world.environment.patches {
            let x = (patch.x / self.world.environment.width as f32) as f64 * width;
            let y = (patch.y / self.world.environment.height as f32) as f64 * height;
            let size = 6.0;
            
            let color = if patch.depleted {
                "#333333"
            } else if patch.energy > patch.max_energy * 0.75 {
                "#50C850"
            } else if patch.energy > patch.max_energy * 0.25 {
                "#C8C850"
            } else {
                "#C85050"
            };
            
            self.ctx.set_fill_style_str(color);
            self.ctx.fill_rect(x - size/2.0, y - size/2.0, size, size);
        }
        
        // Draw threats
        for threat in &self.world.environment.threats {
            if threat.active {
                let x = (threat.x / self.world.environment.width as f32) as f64 * width;
                let y = (threat.y / self.world.environment.height as f32) as f64 * height;
                let radius = (threat.radius / self.world.environment.width as f32) as f64 * width;
                
                self.ctx.set_fill_style_str("rgba(255, 50, 50, 0.2)");
                self.ctx.begin_path();
                self.ctx.arc(x, y, radius, 0.0, 2.0 * std::f64::consts::PI)?;
                self.ctx.fill();
                
                self.ctx.set_fill_style_str("#FF3232");
                self.ctx.begin_path();
                self.ctx.arc(x, y, 5.0, 0.0, 2.0 * std::f64::consts::PI)?;
                self.ctx.fill();
            }
        }
        
        // Draw agents
        for agent in self.world.agents.values() {
            if !agent.alive {
                continue;
            }
            
            let x = (agent.x / self.world.environment.width as f32) as f64 * width;
            let y = (agent.y / self.world.environment.height as f32) as f64 * height;
            let size = 4.0;
            
            let color = match agent.role {
                Role::Founder => "#FFD700",
                Role::Scout => "#00CED1",
                Role::Builder => "#32CD32",
                Role::Attester => "#FF00FF",
                Role::Forager => "#4169E1",
                Role::Broadcaster => "#00CED1",
                Role::Explorer => "#FFD700",
                Role::Healer => "#32CD32",
                Role::Signal => "#FFA500",
                Role::Observer => "#666666",
                _ => "#FFFFFF",
            };
            
            let actual_color = if agent.is_rogue {
                "#FF0000"
            } else if agent.energy < 25.0 {
                "#FF6644"
            } else {
                color
            };
            
            self.ctx.set_fill_style_str(actual_color);
            self.ctx.begin_path();
            self.ctx.arc(x, y, size, 0.0, 2.0 * std::f64::consts::PI)?;
            self.ctx.fill();
            
            // Draw energy ring
            let energy_pct = agent.energy / 100.0;
            self.ctx.set_stroke_style_str("rgba(255,255,255,0.3)");
            self.ctx.set_line_width(1.0);
            self.ctx.begin_path();
            self.ctx.arc(x, y, size + 3.0, -std::f64::consts::FRAC_PI_2, 2.0 * std::f64::consts::PI * energy_pct as f64 - std::f64::consts::FRAC_PI_2)?;
            self.ctx.stroke();
        }
        
        // Draw claims and connections to agents
        for claim in self.world.claims.values() {
            // Find the agent who made the claim
            if let Some(agent) = self.world.agents.get(&claim.agent_id) {
                if !agent.alive {
                    continue;
                }

                // Agent position (scaled)
                let ax = (agent.x / 100.0) as f64 * width;
                let ay = (agent.y / 100.0) as f64 * height;

                // Claim position (scaled)
                let cx = (claim.x / 100.0) as f64 * width;
                let cy = (claim.y / 100.0) as f64 * height;

                // Draw the line connecting agent to claim
                self.ctx.begin_path();
                self.ctx.move_to(ax, ay);
                self.ctx.line_to(cx, cy);

                // Style the line based on claim lens
                let line_color = match claim.lens {
                    Lens::Fact => "rgba(255, 255, 255, 0.4)", // White for facts
                    Lens::Opinion => "rgba(255, 255, 0, 0.25)", // Yellow for opinions
                    Lens::Counter => "rgba(255, 0, 0, 0.3)",   // Red for counters
                    _ => "rgba(100, 100, 100, 0.2)",         // Grey for others
                };
                self.ctx.set_stroke_style_str(line_color);
                self.ctx.set_line_width(1.0);
                self.ctx.stroke();

                // Draw the claim itself as a small square
                let claim_color = match claim.lens {
                    Lens::Fact => "#FFFFFF",
                    Lens::Opinion => "#FFFF00",
                    Lens::Counter => "#FF0000",
                    _ => "#888888",
                };
                self.ctx.set_fill_style_str(claim_color);
                self.ctx.fill_rect(cx - 2.0, cy - 2.0, 4.0, 4.0);
            }
        }

        // Draw stats
        let alive = self.world.agents.values().filter(|a| a.alive).count();
        let claims = self.world.claims.len();
        let counters = self.world.claims.values().filter(|c| c.lens == Lens::Counter).count();
        let health = self.world.environment.metrics.overall_health;
        
        let stats = format!(
            "👥 {} | 📋 {} | 🔍 {} | 🌿 {:.3}",
            alive, claims, counters, health
        );

        self.ctx.set_fill_style_str("#CCCCCC");
        self.ctx.set_font("14px monospace");
        self.ctx.fill_text(&stats, 10.0, 30.0)?;
        
        // Tick counter
        let tick_text = format!("Tick: {}", self.world.tick);
        self.ctx.fill_text(&tick_text, 10.0, 50.0)?;
        
        // Season indicator
        let season = if self.world.environment.season_factor() > 1.0 { "☀️ Rich" } else { "☁️ Poor" };
        self.ctx.fill_text(season, width - 100.0, 30.0)?;
        
        Ok(())
    }
    
    pub fn get_stats(&self) -> JsValue {
        let alive = self.world.agents.values().filter(|a| a.alive).count();
        let claims = self.world.claims.len();
        let counters = self.world.claims.values().filter(|c| c.lens == Lens::Counter).count();
        let health = self.world.environment.metrics.overall_health;

        serde_wasm_bindgen::to_value(&serde_json::json!({
            "agents": alive,
            "claims": claims,
            "counters": counters,
            "health": health,
            "tick": self.world.tick,
            "season": if self.world.environment.season_factor() > 1.0 { "Rich" } else { "Poor" },
        }))
        .unwrap_or_else(|_| JsValue::NULL)
    }

    #[wasm_bindgen(js_name = export_state)]
    pub fn export_state(&self) -> Result<String, JsValue> {
        // World isn't Serialize (contains StdRng etc.), so build a JSON snapshot manually.
        let agents: Vec<_> = self.world.agents.values().map(|a| serde_json::json!({
            "id": a.scp_id,
            "x": a.x,
            "y": a.y,
            "energy": a.energy,
            "role": a.role,
            "alive": a.alive,
            "is_rogue": a.is_rogue,
            "tasks_done": a.tasks_done,
        })).collect();

        let claims: Vec<_> = self.world.claims.values().map(|c| serde_json::json!({
            "id": c.id,
            "x": c.x,
            "y": c.y,
            "agent_id": c.agent_id,
            "kind": c.kind,
            "lens": c.lens,
            "strength": c.strength,
            "tick": c.tick,
        })).collect();

        let state = serde_json::json!({
            "tick": self.world.tick,
            "health": self.world.environment.metrics.overall_health,
            "agents": agents,
            "claims": claims,
        });

        to_string_pretty(&state)
            .map_err(|e| JsValue::from_str(&format!("Failed to serialize world: {}", e)))
    }
}
