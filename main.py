import tkinter as tk
from ui.main_window import MainWindow


def main():
    """Main entry point"""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()