from pathlib import Path
from cefpython3 import cefpython as cef
from CIMXMLParser import *
from PandaPowerManager import *
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog

# Get the current file's directory
CURRENT_DIR = Path(__file__).resolve().parent

# Define the relative path to the asset folder
ASSETS_PATH = CURRENT_DIR / "assets" / "frame0"

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def create_new_window():
    # Get EQ and SSH file paths from entry fields
    eq_path = eq_entry.get()
    ssh_path = ssh_entry.get()

    # Check if EQ and SSH paths are provided
    if eq_path and ssh_path:

        try:
            # Parse XML EQ and SSH
            parser = CIM_XML_parser(eq_path, ssh_path)
            equipmentID_dict, equipment_dict = parser.run()
        except:
            messagebox.showerror("Error", "Could not Parse Files")

        try:
            # Create pandaPower manager
            pandaBear = PandaPowerWriter(dictEquipmentIDtoType=equipmentID_dict, dictEquipment=equipment_dict)
            pandaBear.initialiseNetwork()
            pandaBear.toHTML()
        except:
            messagebox.showerror("Error", "Could not Create PandaPower Network")

        #open window
        cef.Initialize()
        browser = cef.CreateBrowserSync(url="file:///htmlOutput/network.html",
                                        window_title='Results')
        cef.MessageLoop()
        cef.Shutdown()
    else:
        # Show an error message if EQ and SSH paths are not provided
        messagebox.showerror("Error", "Please provide EQ and SSH file paths.")

def browse_file(entry_field):
    # Open file dialog to select a file
    file_path = filedialog.askopenfilename(filetypes=[("XML Files", "*.xml")])
    # Update the entry field with the selected file path
    entry_field.delete(0, END)
    entry_field.insert(END, file_path)

window = Tk()
window.geometry("1195x706")
window.configure(bg="#F2F2F2")

canvas = Canvas(
    window,
    bg="#F2F2F2",
    height=706,
    width=1195,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas.place(x=0, y=0)


canvas.create_rectangle(
    300.0,
    104.0,
    895.0,
    367.0,
    outline="#000000",
    width=1
)


button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=create_new_window,
    relief="flat"
)
button_1.place(
    x=512.8718872070312,
    y=395.3599853515625,
    width=170.10675048828125,
    height=49.8353271484375
)

canvas.create_text(
    320.0,
    189.0,
    anchor="nw",
    text="EQ File:",
    fill="#000000",
    font=("Roboto", 20 * -1)
)

canvas.create_text(
    320.0,
    219.0,
    anchor="nw",
    text="SSH File:",
    fill="#000000",
    font=("Roboto", 20 * -1)
)

canvas.create_text(
    597.0,
    115.0,
    anchor="center",
    text="Input Data",
    fill="#000000",
    font=("Roboto", 20 * -1)
)

canvas.create_text(
    500.0,
    57.0,
    anchor="nw",
    text="CIM-XML Parser",
    fill="#000000",
    font=("Roboto Bold", 24 * -1)
)

# Entry fields for EQ and SSH paths
eq_entry = Entry(window, width=70)
eq_entry.place(x=420, y=189)

ssh_entry = Entry(window, width=70)
ssh_entry.place(x=420, y=219)

# Browse buttons to select EQ and SSH files
eq_browse_button = Button(
    text="Browse",
    command=lambda: browse_file(eq_entry),
    relief="flat"
)
eq_browse_button.place(x=840, y=185)

ssh_browse_button = Button(
    text="Browse",
    command=lambda: browse_file(ssh_entry),
    relief="flat"
)
ssh_browse_button.place(x=840, y=215)

window.resizable(False, False)
window.mainloop()

