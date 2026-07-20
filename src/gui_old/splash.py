import customtkinter as ctk

from core.settings import PROJECT_NAME


class Splash(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)

        self.overrideredirect(True)

        # Window settings
        width, height = 320, 140
        scaling = ctk.ScalingTracker.get_window_scaling(self)
        x = (self.winfo_screenwidth() - width) * scaling / 2
        y = (self.winfo_screenheight() - height) * scaling / 2
        self.geometry(f"{width}x{height}+{int(x)}+{int(y)}")

        # Theme
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("green")

        # Setup ui
        ctk.CTkLabel(
            self, text=f"{PROJECT_NAME}", font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=20)

        self.status_label = ctk.CTkLabel(
            self, text="Start loading...", wraplength=250, font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=4)

        self.progress = ctk.CTkProgressBar(self, width=260)
        self.progress.pack(pady=4)
        self.progress.set(0)

        self.update()

    def loading_modules(self, modules: list[str]):
        for i, module in enumerate(modules):
            try:
                self.status_label.configure(
                    text=f"Module {module.title()} is loading..."
                )
                self.update()
                __import__(module)
                self.progress.set((i + 1) / len(modules))
                self.update()
            except ImportError:
                raise ImportError(f"Module {module} not found!")
