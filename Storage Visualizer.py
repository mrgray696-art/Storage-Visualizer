import tkinter as tk
from tkinter import ttk
import psutil

FONT			= "Helvetica"
FONT_SIZE		= 9

def bytes_to_gb( bytes_val ):
	return bytes_val / ( 1024 ** 3 )

def get_drive_details():
	drives = []
	total_bytes = 0
	used_bytes = 0
	for partition in psutil.disk_partitions( all = False ):
		if 'cdrom' in partition.opts or partition.fstype == '':
			continue
		try:
			usage = psutil.disk_usage( partition.mountpoint )
			drives.append( { "device": partition.device or partition.mountpoint, "mountpoint": partition.mountpoint, "total": usage.total, "used": usage.used, "percent": usage.percent } )
			total_bytes += usage.total
			used_bytes += usage.used
		except PermissionError:
			continue
	return drives, total_bytes, used_bytes

def create_usage_block( parent, title, total_b, used_b, percent ):
	block = ttk.LabelFrame( parent, text = title, padding = "5" )
	block.pack( fill = tk.X, expand = True, pady = 5, padx = 5 )
	
	pbar = ttk.Progressbar( block, orient = "horizontal", mode = "determinate" )
	pbar.pack( fill = tk.X, pady = ( 1, 6 ) )
	pbar[ "value" ] = percent
	
	u_gb = bytes_to_gb( used_b )
	f_gb = bytes_to_gb( total_b - used_b )
	t_gb = bytes_to_gb( total_b )
	free_percent = 100.0 - percent if total_b > 0 else 0.0

	# Frame container for the grid
	grid_frame = ttk.Frame( block )
	grid_frame.pack( fill = tk.X, expand = True )

	# Configure 3 equal-width columns that stretch to fill the container
	grid_frame.columnconfigure( 0, weight = 1 )
	grid_frame.columnconfigure( 1, weight = 1 )
	grid_frame.columnconfigure( 2, weight = 1 )

	# Row 0: Used
	ttk.Label( grid_frame, text = f"{u_gb:.1f} GB", font = ( FONT, FONT_SIZE ) ).grid( row = 0, column = 0, sticky = "w" )
	ttk.Label( grid_frame, text = f"{percent:.2f}%", font = ( FONT, FONT_SIZE ) ).grid( row = 0, column = 1, sticky = "w" )
	ttk.Label( grid_frame, text = "Used", font = ( FONT, FONT_SIZE ) ).grid( row = 0, column = 2, sticky = "w" )

	# Row 1: Free
	ttk.Label( grid_frame, text = f"{f_gb:.1f} GB", font = ( FONT, FONT_SIZE ) ).grid( row = 1, column = 0, sticky = "w" )
	ttk.Label( grid_frame, text = f"{free_percent:.2f}%", font = ( FONT, FONT_SIZE ) ).grid( row = 1, column = 1, sticky = "w" )
	ttk.Label( grid_frame, text = "Free", font = ( FONT, FONT_SIZE ) ).grid( row = 1, column = 2, sticky = "w" )

	# Row 2: Total
	ttk.Label( grid_frame, text = f"{t_gb:.1f} GB", font = ( FONT, FONT_SIZE ) ).grid( row = 2, column = 0, sticky = "w" )
	ttk.Label( grid_frame, text = "", font = ( FONT, FONT_SIZE ) ).grid( row = 2, column = 1, sticky = "w" )
	ttk.Label( grid_frame, text = "Total", font = ( FONT, FONT_SIZE ) ).grid( row = 2, column = 2, sticky = "w" )

	return block

def create_app():
	root = tk.Tk()
	root.title( "Storage Overview" )
	root.geometry( "300x300" )
	root.minsize( 300, 300 )
	drives, total_b, used_b = get_drive_details()
	overall_percent = ( used_b / total_b ) * 100 if total_b > 0 else 0
	
	main_frame = ttk.Frame( root, padding = "5" )
	main_frame.pack( fill = tk.BOTH, expand = True )

	# # Overall Block
	summary_frame = ttk.Frame( main_frame )
	summary_frame.pack( fill = tk.X, pady = ( 0, 5 ) )
	create_usage_block( summary_frame, title = "All Storage Combined", total_b = total_b, used_b = used_b, percent = overall_percent )

	# # Breakdown Block
	breakdown_label = ttk.Label( main_frame, text = "Breakdown", font = ( "Helvetica", 10, "bold" ) )
	breakdown_label.pack( pady = ( 0, 5 ) )
	
	list_container = ttk.Frame( main_frame )
	list_container.pack( fill = tk.BOTH, expand = True )
	
	canvas = tk.Canvas( list_container, highlightthickness = 0 )
	scrollbar = ttk.Scrollbar( list_container, orient = "vertical", command = canvas.yview )
	
	scrollable_frame = ttk.Frame( canvas )
	scrollable_frame.bind( "<Configure>", lambda e: canvas.configure( scrollregion = canvas.bbox( "all" ) ) )
	
	canvas_window = canvas.create_window( ( 0, 0 ), window = scrollable_frame, anchor = "nw" )
	canvas.bind( "<Configure>", lambda event: canvas.itemconfig( canvas_window, width = event.width ) )
	canvas.configure( yscrollcommand = scrollbar.set )

	# Layout Canvas and Scrollbar side by side
	scrollbar.pack( side = tk.LEFT, fill = tk.Y )
	canvas.pack( side = tk.RIGHT, fill = tk.BOTH, expand = True )
	

	def _on_mousewheel( event ):
		canvas.yview_scroll( int( -1 * ( event.delta / 120 ) ), "units" )
	canvas.bind_all( "<MouseWheel>", _on_mousewheel )
	
	for drive in drives:
		create_usage_block( scrollable_frame, title = f"Drive {drive['device']}", total_b = drive['total'], used_b = drive['used'], percent = drive['percent'] )

	root.mainloop()

if __name__ == "__main__":
	create_app()