py library - pillow

	---CMD Based---
hiding text - 
py imgstego.py hide [inserted.png] [modified.png] "secret message here" [pass I make up]

hiding a file - 
py imgstego.py hidefile [inserted.png] [modified.png] [hidden file (zip preff for smaller size)] [pass I make up]

reveal - 
py imgstego.py reveal [modified.png] [pass I make up] > recovered.txt
							^^^^^^^^^^^^^-> shows output to selected file, and if hidden a file, it changes to the right format
reveal to screen-
py imgstego.py reveal [modified.png] s3cr3t

#also, if the "> recovered.txt" isn't prompted, it will show on the console

	---GUI Based---
hiding text -
top option - choose hide
#
#

reveal -
top option - choose reveal
choose image with injected text or file

tips -
Use PNG/BMP. JPEG will likely corrupt the payload.

Capacity (rule of thumb): ~4 bits per pixel for RGBA PNG.
1920×1080 ≈ ~2.5–3 MB payload max (practical).

Don’t let apps recompress. Many messengers/websites recompress images (kills hidden data). Share files as-is (e.g., zip them first).



