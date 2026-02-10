import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

def show_image_popup(
    title="Image Viewer",
    image_path=None
):
    """
    Display a fullscreen popup showing an image.
    Press ESC to exit fullscreen or click 'Close' to quit.
    """

    def exit_fullscreen(event=None):
        root.attributes('-fullscreen', False)

    def close_window():
        root.destroy()

    # === Initialize window ===
    root = tk.Tk()
    root.title(title)
    root.attributes('-fullscreen', True)
    root.bind("<Escape>", exit_fullscreen)

    # === Screen size ===
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # === Main frame ===
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill="both", expand=True)

    # === Image display ===
    if image_path:
        try:
            img = Image.open(image_path)

            # Fit image to screen (keeping aspect ratio)
            img_ratio = img.height / img.width
            target_width = screen_width - 100
            target_height = int(target_width * img_ratio)

            # If image too tall, scale by height instead
            if target_height > screen_height - 150:
                target_height = screen_height - 150
                target_width = int(target_height / img_ratio)

            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            image_label = ttk.Label(main_frame, image=photo)
            image_label.image = photo
            image_label.pack(expand=True)
        except Exception as e:
            print(f"Error loading image: {e}")
            ttk.Label(main_frame, text="Error loading image.", font=("Arial", 24)).pack(expand=True)

    # === Bottom Close Button ===
    ttk.Button(
        main_frame,
        text="Confirm",
        command=close_window
    ).pack(padx=40,pady=40)

    root.mainloop()

def show_checkbox_popup(
    options,
    title="Select Options",
    image_path=None
):
    selected_options = []

    def toggle_all():
        state = select_all_var.get()
        for var in checkbox_vars:
            var.set(state)

    def on_submit():
        nonlocal selected_options
        selected_options = [
            options[i] for i, var in enumerate(checkbox_vars) if var.get()
        ]
        root.destroy()

    def exit_fullscreen(event=None):
        root.attributes('-fullscreen', False)

    # === Initialize window ===
    root = tk.Tk()
    root.title(title)
    root.attributes('-fullscreen', True)
    root.bind("<Escape>", exit_fullscreen)

    # === Font ===
    font_style = ("Arial", 24)

    # === Screen size ===
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # === Main frame ===
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill="both", expand=True)

    # Grid configuration: left (fixed), right (stretch)
    main_frame.columnconfigure(0, weight=0)
    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(0, weight=1)

    # === LEFT COLUMN: Fixed width for 60 characters ===
    char_width_px = 12  # estimate for 24pt font
    target_width = 40 * char_width_px  # ~840 px

    checkbox_frame = ttk.Frame(main_frame, width=target_width)
    checkbox_frame.grid(row=0, column=0, sticky="nsw", padx=(0, 20))
    checkbox_frame.grid_rowconfigure(99, weight=1)
    checkbox_frame.grid_propagate(False)

    # "Select All"
    select_all_var = tk.BooleanVar()
    tk.Checkbutton(
        checkbox_frame,
        text="{}".format(title),
        variable=select_all_var,
        command=toggle_all,
        font=font_style
    ).grid(row=0, column=0, sticky="w", pady=(0, 10))

    # Checkboxes with auto-wrapping labels
    checkbox_vars = []
    for i, opt in enumerate(options, start=1):
        var = tk.BooleanVar()
        tk.Checkbutton(
            checkbox_frame,
            text=opt,
            variable=var,
            font=font_style,
            wraplength=target_width - 40,  # wrap to fit inside column
            justify="left"
        ).grid(row=i, column=0, sticky="w", pady=4)
        checkbox_vars.append(var)

    # Submit button at bottom-left
    tk.Button(
        checkbox_frame,
        text="Submit",
        command=on_submit,
        font=font_style
    ).grid(row=99, column=0, sticky="sw", pady=(20, 0))

    # === RIGHT COLUMN: Image ===
    if image_path:
        try:
            img = Image.open(image_path)

            # Set width to 2/3 of screen, minus padding
            img_width = int((screen_width * 2 / 3) - 100)
            img_ratio = img.height / img.width
            img_height = int(img_width * img_ratio)

            # Clamp if too tall
            if img_height > screen_height - 100:
                img_height = screen_height - 100
                img_width = int(img_height / img_ratio)

            img = img.resize((img_width, img_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            image_label = ttk.Label(main_frame, image=photo)
            image_label.image = photo
            image_label.grid(row=0, column=1, sticky="nsew", padx=40)
        except Exception as e:
            print(f"Error loading image: {e}")

    root.mainloop()
    return selected_options


def show_input_popup(
    title="Scan QR Code",
    image_path=None,
    prompt="Scan FEMB QR Code:",
    require_confirmation=True
):
    """
    Display a fullscreen popup showing an image with a text input field for QR scanning.
    If require_confirmation is True, user must scan twice to confirm.
    Press ESC to exit fullscreen.
    Returns the scanned value, or empty string if skipped/cancelled.
    """
    result = {"value": ""}

    def exit_fullscreen(event=None):
        root.attributes('-fullscreen', False)

    def close_window():
        root.destroy()

    def on_skip():
        result["value"] = ""
        root.destroy()

    def show_confirm_button():
        """Show confirm button after successful match"""
        # Hide entry and other buttons
        entry.config(state="disabled")
        submit_btn.pack_forget()
        skip_btn.pack_forget()

        # Show confirm button
        confirm_btn = tk.Button(
            button_frame,
            text="Confirm",
            command=root.destroy,
            font=("Arial", 24, "bold"),
            width=15,
            bg="#4CAF50",
            fg="white"
        )
        confirm_btn.pack(pady=10)
        confirm_btn.focus_set()

    def on_submit(event=None):
        value = entry_var.get().strip().replace('/', '_')

        if value == "":
            # Empty = skip
            status_label.config(text="Slot will be skipped (empty)", foreground="orange")
            result["value"] = ""
            root.after(800, root.destroy)
            return

        if len(value) < 3:
            status_label.config(text="ID too short! Please scan again.", foreground="red")
            entry_var.set("")
            entry.focus_set()
            return

        if require_confirmation:
            if not hasattr(on_submit, 'first_scan') or on_submit.first_scan is None:
                # First scan
                on_submit.first_scan = value
                entry_var.set("")
                prompt_label.config(text="Scan again to confirm:")
                status_label.config(text=f"First scan: {value}", foreground="blue")
                entry.focus_set()
            else:
                # Second scan - check match
                if value == on_submit.first_scan:
                    result["value"] = value
                    status_label.config(text=f"ID Matched: {value}", foreground="green")
                    prompt_label.config(text="Click Confirm to proceed")
                    entry_var.set(value)
                    show_confirm_button()
                else:
                    status_label.config(
                        text=f"Mismatch! ({on_submit.first_scan} vs {value}) - Try again",
                        foreground="red"
                    )
                    on_submit.first_scan = None
                    entry_var.set("")
                    prompt_label.config(text=prompt)
                    entry.focus_set()
        else:
            result["value"] = value
            root.destroy()

    on_submit.first_scan = None

    # === Initialize window ===
    root = tk.Tk()
    root.title(title)
    root.attributes('-fullscreen', True)
    root.bind("<Escape>", exit_fullscreen)

    # === Font ===
    font_large = ("Arial", 28)
    font_medium = ("Arial", 20)

    # === Screen size ===
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # === Main frame ===
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill="both", expand=True)

    # Grid: left column for input, right column for image
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=2)
    main_frame.rowconfigure(0, weight=1)

    # === LEFT COLUMN: Input area ===
    input_frame = ttk.Frame(main_frame)
    input_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 40))

    # Title label
    title_label = tk.Label(input_frame, text=title, font=("Arial", 32, "bold"))
    title_label.pack(pady=(50, 30))

    # Prompt label
    prompt_label = tk.Label(input_frame, text=prompt, font=font_large)
    prompt_label.pack(pady=(20, 10))

    # Entry field for QR scanning
    entry_var = tk.StringVar()
    entry = tk.Entry(input_frame, textvariable=entry_var, font=font_large, width=30, justify="center")
    entry.pack(pady=10, ipady=10)
    entry.bind("<Return>", on_submit)
    entry.focus_set()



    # Status label for feedback
    status_label = tk.Label(input_frame, text="Scan QR code or press Enter to skip", font=font_medium)
    status_label.pack(pady=(10, 10))

    # Notification label below text box
    notification_label = tk.Label(
        input_frame,
        text="After Scan, Please connect the FEMB and insert into certain Slot",
        font=("Arial", 18),
        fg="blue"
    )
    notification_label.pack(pady=(10, 10))

    # Buttons frame
    button_frame = ttk.Frame(input_frame)
    button_frame.pack(pady=30)

    submit_btn = tk.Button(
        button_frame,
        text="Submit",
        command=on_submit,
        font=font_medium,
        width=12
    )
    submit_btn.pack(side="left", padx=10)

    skip_btn = tk.Button(
        button_frame,
        text="Skip (Empty)",
        command=on_skip,
        font=font_medium,
        width=12
    )
    skip_btn.pack(side="left", padx=10)

    # === RIGHT COLUMN: Image ===
    if image_path:
        try:
            img = Image.open(image_path)

            # Set width to ~60% of screen
            img_width = int(screen_width * 0.55)
            img_ratio = img.height / img.width
            img_height = int(img_width * img_ratio)

            # Clamp if too tall
            if img_height > screen_height - 100:
                img_height = screen_height - 100
                img_width = int(img_height / img_ratio)

            img = img.resize((img_width, img_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            image_label = ttk.Label(main_frame, image=photo)
            image_label.image = photo
            image_label.grid(row=0, column=1, sticky="nsew", padx=20)
        except Exception as e:
            print(f"Error loading image: {e}")

    root.mainloop()
    return result["value"]


def show_removal_popup(
    title="Remove FEMB",
    image_path=None,
    expected_id="",
    test_status="pass"
):
    """
    Display a fullscreen popup for board removal with:
    - Image showing disconnection instructions
    - Test result (PASS/FAIL)
    - QR scan confirmation field
    - Tray placement instruction

    Returns True if ID matched and confirmed, False if cancelled.
    """
    result = {"confirmed": False}

    def exit_fullscreen(event=None):
        root.attributes('-fullscreen', False)

    def on_cancel():
        result["confirmed"] = False
        root.destroy()

    def on_confirm():
        """Called when ID is matched and user clicks confirm"""
        result["confirmed"] = True
        root.destroy()

    def on_submit(event=None):
        value = entry_var.get().strip().replace('/', '_')

        if value == "":
            status_label.config(text="Please scan the FEMB QR code!", foreground="red")
            entry.focus_set()
            return

        if value == expected_id:
            # ID matched - show confirm button
            status_label.config(text=f"ID Matched: {value}")
            entry.config(state="disabled")
            submit_btn.pack_forget()

            # Show confirm button - green for pass, orange for fail/other
            btn_color = "#4CAF50" if test_status == 'pass' else "#FF8C00"
            confirm_btn = tk.Button(
                button_frame,
                text="Confirm & Remove",
                command=on_confirm,
                font=("Arial", 24, "bold"),
                width=20,
                bg=btn_color,
                fg="white"
            )
            confirm_btn.pack(pady=10)
            confirm_btn.focus_set()
        else:
            status_label.config(
                text=f"ID Mismatch! Expected: {expected_id}, Scanned: {value}",
                foreground="red"
            )
            entry_var.set("")
            entry.focus_set()

    # === Initialize window ===
    root = tk.Tk()
    root.title(title)
    root.attributes('-fullscreen', True)
    root.bind("<Escape>", exit_fullscreen)

    # === Font ===
    font_large = ("Arial", 28)
    font_medium = ("Arial", 20)

    # === Screen size ===
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # === Main frame ===
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill="both", expand=True)

    # Grid: left column for info/input, right column for image
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=2)
    main_frame.rowconfigure(0, weight=1)

    # === LEFT COLUMN: Info and Input area ===
    input_frame = ttk.Frame(main_frame)
    input_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 40))

    # Title label
    title_label = tk.Label(input_frame, text=title, font=("Arial", 32, "bold"))
    title_label.pack(pady=(30, 20))

    # FEMB ID display
    id_label = tk.Label(input_frame, text=f"FEMB ID: {expected_id}", font=font_large)
    id_label.pack(pady=(10, 10))

    # Test result display with color
    if test_status == 'pass':
        result_text = "Test Result: PASS"
        result_color = "green"
        tray_text = "Place in GOOD tray"
        tray_color = "green"
    elif test_status == 'fail':
        result_text = "Test Result: FAIL"
        result_color = "red"
        tray_text = "Place in BAD tray"
        tray_color = "red"
    else:
        result_text = "Test Result: NO DATA"
        result_color = "orange"
        tray_text = "Place in REVIEW tray"
        tray_color = "orange"

    result_label = tk.Label(
        input_frame,
        text=result_text,
        font=("Arial", 36, "bold"),
        fg=result_color
    )
    result_label.pack(pady=(20, 10))

    # Tray instruction
    tray_label = tk.Label(
        input_frame,
        text=tray_text,
        font=("Arial", 28, "bold"),
        fg=tray_color
    )
    tray_label.pack(pady=(10, 30))

    # Separator
    ttk.Separator(input_frame, orient="horizontal").pack(fill="x", pady=20)

    # Prompt label
    prompt_label = tk.Label(input_frame, text="Scan FEMB QR Code to confirm:", font=font_medium)
    prompt_label.pack(pady=(10, 10))

    # Entry field for QR scanning
    entry_var = tk.StringVar()
    entry = tk.Entry(input_frame, textvariable=entry_var, font=font_large, width=30, justify="center")
    entry.pack(pady=10, ipady=10)
    entry.bind("<Return>", on_submit)
    entry.focus_set()

    # Status label for feedback
    status_label = tk.Label(input_frame, text="Scan QR code to verify FEMB ID", font=font_medium)
    status_label.pack(pady=(10, 10))

    # Buttons frame
    button_frame = ttk.Frame(input_frame)
    button_frame.pack(pady=30)

    submit_btn = tk.Button(
        button_frame,
        text="Submit",
        command=on_submit,
        font=font_medium,
        width=12
    )
    submit_btn.pack(pady=10)

    # === RIGHT COLUMN: Image ===
    if image_path:
        try:
            img = Image.open(image_path)

            # Set width to ~55% of screen
            img_width = int(screen_width * 0.55)
            img_ratio = img.height / img.width
            img_height = int(img_width * img_ratio)

            # Clamp if too tall
            if img_height > screen_height - 100:
                img_height = screen_height - 100
                img_width = int(img_height / img_ratio)

            img = img.resize((img_width, img_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            image_label = ttk.Label(main_frame, image=photo)
            image_label.image = photo
            image_label.grid(row=0, column=1, sticky="nsew", padx=20)
        except Exception as e:
            print(f"Error loading image: {e}")

    root.mainloop()
    return result["confirmed"]
