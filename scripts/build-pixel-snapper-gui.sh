#!/usr/bin/env bash
set -euo pipefail

# Run from the Pixel Snapper source directory.
test -f Cargo.toml || { echo "Cargo.toml not found; run from the Pixel Snapper repository root." >&2; exit 1; }
test -f src/lib.rs || { echo "src/lib.rs not found; refusing to create a replacement library." >&2; exit 1; }

python3 <<'PY'
from pathlib import Path
import re

cargo = Path("Cargo.toml")
text = cargo.read_text(encoding="utf-8")

match = re.search(r"(?m)^\[dependencies\]\s*$", text)
if not match:
    raise SystemExit("Cargo.toml has no [dependencies] section.")

required = [
    ("eframe", 'eframe = { version = "0.29", default-features = true }'),
    ("rfd", 'rfd = "0.15"'),
]

missing = [
    line for name, line in required
    if not re.search(rf"(?m)^\s*{re.escape(name)}\s*=", text)
]

if missing:
    insert_at = match.end()
    text = text[:insert_at] + "\n" + "\n".join(missing) + text[insert_at:]

if 'name = "pixel-snapper-gui"' not in text:
    text += '''

[[bin]]
name = "pixel-snapper-gui"
path = "src/bin/pixel_snapper_gui.rs"
'''

cargo.write_text(text, encoding="utf-8")

lib = Path("src/lib.rs")
lib_text = lib.read_text(encoding="utf-8")

if "pub fn process_image_bytes_for_gui" not in lib_text:
    lib_text += r"""

// Native GUI entry point. This reuses the crate's existing processing pipeline.
#[cfg(not(target_arch = "wasm32"))]
pub fn process_image_bytes_for_gui(
    input_bytes: &[u8],
    k_colors: usize,
    pixel_size_override: Option<f64>,
) -> Result<Vec<u8>> {
    let mut config = Config::default();
    config.k_colors = k_colors;
    config.pixel_size_override = pixel_size_override;
    let processed = process_image_common(input_bytes, Some(config))?;
    Ok(processed.output_bytes)
}
"""
    lib.write_text(lib_text, encoding="utf-8")
PY

mkdir -p src/bin
cat > src/bin/pixel_snapper_gui.rs <<'RS'
use eframe::egui;
use std::path::PathBuf;

struct PixelSnapperApp {
    input_path: Option<PathBuf>,
    input_bytes: Option<Vec<u8>>,
    input_texture: Option<egui::TextureHandle>,
    output_texture: Option<egui::TextureHandle>,
    output_bytes: Option<Vec<u8>>,
    k_colors: usize,
    pixel_size: f64,
    use_pixel_size: bool,
    status: String,
}

impl Default for PixelSnapperApp {
    fn default() -> Self {
        Self {
            input_path: None,
            input_bytes: None,
            input_texture: None,
            output_texture: None,
            output_bytes: None,
            k_colors: 16,
            pixel_size: 8.0,
            use_pixel_size: false,
            status: "Choose a PNG or JPEG image to begin.".to_owned(),
        }
    }
}

impl PixelSnapperApp {
    fn texture_from_bytes(
        ctx: &egui::Context,
        bytes: &[u8],
        name: &str,
    ) -> Result<egui::TextureHandle, String> {
        let decoded = image::load_from_memory(bytes)
            .map_err(|e| format!("Could not decode image: {e}"))?
            .to_rgba8();
        let size = [decoded.width() as usize, decoded.height() as usize];
        let image = egui::ColorImage::from_rgba_unmultiplied(size, decoded.as_raw());
        Ok(ctx.load_texture(name, image, egui::TextureOptions::NEAREST))
    }

    fn open_image(&mut self, ctx: &egui::Context) {
        if let Some(path) = rfd::FileDialog::new()
            .add_filter("Images", &["png", "jpg", "jpeg"])
            .pick_file()
        {
            match std::fs::read(&path) {
                Ok(bytes) => match Self::texture_from_bytes(ctx, &bytes, "input") {
                    Ok(texture) => {
                        self.input_path = Some(path);
                        self.input_bytes = Some(bytes);
                        self.input_texture = Some(texture);
                        self.output_texture = None;
                        self.output_bytes = None;
                        self.status = "Image loaded.".to_owned();
                    }
                    Err(error) => self.status = error,
                },
                Err(error) => self.status = format!("Could not read file: {error}"),
            }
        }
    }

    fn process(&mut self, ctx: &egui::Context) {
        let Some(bytes) = self.input_bytes.as_deref() else {
            self.status = "Choose an input image first.".to_owned();
            return;
        };
        let override_size = self.use_pixel_size.then_some(self.pixel_size);
        match spritefusion_pixel_snapper::process_image_bytes_for_gui(
            bytes,
            self.k_colors,
            override_size,
        ) {
            Ok(output) => match Self::texture_from_bytes(ctx, &output, "output") {
                Ok(texture) => {
                    self.output_bytes = Some(output);
                    self.output_texture = Some(texture);
                    self.status = "Processing complete.".to_owned();
                }
                Err(error) => self.status = error,
            },
            Err(error) => self.status = format!("Processing failed: {error}"),
        }
    }

    fn save_output(&mut self) {
        let Some(bytes) = self.output_bytes.as_ref() else {
            self.status = "Process an image before saving.".to_owned();
            return;
        };
        if let Some(path) = rfd::FileDialog::new()
            .add_filter("PNG image", &["png"])
            .set_file_name("pixel-snapper-output.png")
            .save_file()
        {
            match std::fs::write(path, bytes) {
                Ok(()) => self.status = "Output saved.".to_owned(),
                Err(error) => self.status = format!("Could not save output: {error}"),
            }
        }
    }
}

impl eframe::App for PixelSnapperApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::TopBottomPanel::top("controls").show(ctx, |ui| {
            ui.horizontal(|ui| {
                if ui.button("Open image").clicked() {
                    self.open_image(ctx);
                }
                if ui.button("Process").clicked() {
                    self.process(ctx);
                }
                if ui.button("Save output").clicked() {
                    self.save_output();
                }
            });
            ui.horizontal(|ui| {
                ui.label("Colours");
                ui.add(egui::Slider::new(&mut self.k_colors, 2..=256));
                ui.checkbox(&mut self.use_pixel_size, "Override pixel size");
                if self.use_pixel_size {
                    ui.add(egui::Slider::new(&mut self.pixel_size, 1.0..=64.0).step_by(0.5));
                }
            });
            ui.label(&self.status);
        });

        egui::CentralPanel::default().show(ctx, |ui| {
            ui.columns(2, |columns| {
                columns[0].heading("Input");
                if let Some(texture) = &self.input_texture {
                    columns[0].add(egui::Image::new(texture).shrink_to_fit());
                } else {
                    columns[0].label("No input image");
                }
                columns[1].heading("Output");
                if let Some(texture) = &self.output_texture {
                    columns[1].add(egui::Image::new(texture).shrink_to_fit());
                } else {
                    columns[1].label("Process an image to preview the result");
                }
            });
        });
    }
}

fn main() -> eframe::Result<()> {
    eframe::run_native(
        "Pixel Snapper",
        eframe::NativeOptions::default(),
        Box::new(|_cc| Ok(Box::new(PixelSnapperApp::default()))),
    )
}
RS

echo "Building Pixel Snapper GUI..."
cargo build --release --bin pixel-snapper-gui
mkdir -p dist
cp target/release/pixel-snapper-gui.exe dist/Pixel-Snapper.exe
echo "Built dist/Pixel-Snapper.exe"
