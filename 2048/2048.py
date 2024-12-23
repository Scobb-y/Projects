import customtkinter as tk

class game2048(tk.CTk):
  def __init__(self):
    super().__init__()
    self.title("2048")
    self.geometry("450x450")
    self.size = 5
    self.tiles = [[None for _ in range(self.size)] for _ in range(self.size)]
    self.createGrid()

  def createGrid(self):
    for row in range(self.size):
      for col in range(self.size):
        frame = tk.CTkFrame(self, width=80, height=80, corner_radius=10)
        frame.grid(row=row, column=col, padx=5, pady=5)
        label = tk.CTkLabel(frame, text="", font=("Helvetica", 24))
        label.place(relx=0.5, rely=0.5, anchor="center")
        self.tiles[row][col] = label

  def updateTile(self, row, col, value):
    tile = self.tiles[row][col]
    tile.configure(text=str(value) if value else "")
    tile.master.configure(fg_color="#eee4da" if value else "#cdc1b4")


if __name__ == "__main__":
  app = game2048()
  app.mainloop()