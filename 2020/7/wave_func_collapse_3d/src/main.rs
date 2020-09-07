extern crate glium;

fn main() {
    let mut events_loop = glium::glutin::event_loop::EventLoop::new();
    let window_builder = glium::glutin::window::WindowBuilder::new()
        .with_inner_size(glium::glutin::dpi::LogicalSize::new(1024.0, 1024.0))
        .with_title("hello world");
    let context_builder = glium::glutin::ContextBuilder::new();
    let _display = glium::Display::new(window_builder, context_builder, &events_loop).unwrap();

    let mut frame = _display.draw();
}
