import bimpy as bp


context = bp.Context()
context.init(600, 600, "Hello, Bimpy!")
label_content = bp.String()
spinner_content = bp.Float()

while not context.should_close():
    with context:
        bp.text("Hello, Bimpy!")

        if bp.button("Ok"):
            print("Hello!")

        bp.input_text("string", label_content, 256)
        bp.slider_float("float", spinner_content, 0.0, 1.0)
