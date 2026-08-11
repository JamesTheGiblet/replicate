//! Replicant WASM - Browser visualization bindings

use std::collections::HashMap;
use wasm_bindgen::prelude::*;
use web_sys::{CanvasRenderingContext2d, HtmlCanvasElement};

// Import the Replicant core
mod replicant_core;
use replicant_core::*;

/// WebAssembly bindings for Replicant
#[wasm_bindgen]
pub struct ReplicantWASM {
    world: World,
    canvas: HtmlCanvasElement,
    ctx: CanvasRenderingContext2d,
    running: bool,
    tick: u32,
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
        
        // Add founders
        let founders = create_founders();
        for (name, agent) in founders {
            // Log in JS console
            web_sys::console::log_1(&format!("Founder: {}", name).into());
        }
        
        Ok(ReplicantWASM {
            world,
            canvas,
            ctx,
            running: false,
            tick: 0,
        })
    }
    
    pub fn start(&mut self) -> Result<(), JsValue> {
        self.running = true;
        self.run_loop()?;
        Ok(())
    }
    
    pub fn pause(&mut self) {
        self.running = !self.running;
    }
    
    pub fn step(&mut self) -> Result<(), JsValue> {
        if !self.running {
            self.world.tick();
            self.tick += 1;
            self.render()?;
        }
        Ok(())
    }
    
    fn run_loop(&mut self) -> Result<(), JsValue> {
        while self.running && self.tick < 1000 {
            self.world.tick();
            self.tick += 1;
            self.render()?;
            
            // Yield to browser event loop
            // Using request_animation_frame would be better, but this is simpler
            // for a demo
            if self.tick % 10 == 0 {
                break;
            }
        }
        Ok(())
    }
    
    fn render(&self) -> Result<(), JsValue> {
        let width = self.canvas.width() as f64;
        let height = self.canvas.height() as f64;
        
        self.ctx.clear_rect(0.0, 0.0, width, height);
        
        // Draw background
        self.ctx.set_fill_style(&"#0B0E14".into());
        self.ctx.fill_rect(0.0, 0.0, width, height);
        
        // Draw resources
        for patch in &self.world.environment.patches {
            let x = (patch.x / 100.0) * width;
            let y = (patch.y / 100.0) * height;
            let size = 6.0;
            
            let color = if patch.depleted {
                "#333333"
            } else if patch.energy > patch.max_energy * 0.7 {
                "#50C850"
            } else if patch.energy > patch.max_energy * 0.3 {
                "#C8C850"
            } else {
                "#C85050"
            };
            
            self.ctx.set_fill_style(&color.into());
            self.ctx.fill_rect(x - size/2.0, y - size/2.0, size, size);
        }
        
        // Draw threats
        for threat in &self.world.environment.threats {
            if threat.active {
                let x = (threat.x / 100.0) * width;
                let y = (threat.y / 100.0) * height;
                let radius = (threat.radius / 100.0) * width;
                
                self.ctx.set_fill_style(&"rgba(255, 50, 50, 0.2)".into());
                self.ctx.begin_path();
                self.ctx.arc(x, y, radius, 0.0, 2.0 * std::f64::consts::PI)?;
                self.ctx.fill();
                
                self.ctx.set_fill_style(&"#FF3232".into());
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
            
            let x = (agent.x / 100.0) * width;
            let y = (agent.y / 100.0) * height;
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
                Role::Signal => "#FF00FF",
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
            
            self.ctx.set_fill_style(&actual_color.into());
            self.ctx.begin_path();
            self.ctx.arc(x, y, size, 0.0, 2.0 * std::f64::consts::PI)?;
            self.ctx.fill();
            
            // Draw energy ring
            let energy_pct = agent.energy / 100.0;
            self.ctx.set_stroke_style(&"rgba(255,255,255,0.3)".into());
            self.ctx.set_line_width(1.0);
            self.ctx.begin_path();
            self.ctx.arc(x, y, size + 3.0, 0.0, 2.0 * std::f64::consts::PI * energy_pct)?;
            self.ctx.stroke();
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
        
        self.ctx.set_fill_style(&"#CCCCCC".into());
        self.ctx.set_font("14px monospace");
        self.ctx.fill_text(&stats, 10.0, 30.0)?;
        
        // Tick counter
        let tick_text = format!("Tick: {}", self.tick);
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
        
        JsValue::from_serde(&serde_json::json!({
            "agents": alive,
            "claims": claims,
            "counters": counters,
            "health": health,
            "tick": self.tick,
            "season": if self.world.environment.season_factor() > 1.0 { "Rich" } else { "Poor" },
        })).unwrap()
    }
}
