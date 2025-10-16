import sys
import os.path

logo_base = "Emmas_owl_logo.png"
if getattr(sys, 'frozen', False):
    bundle_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    logo_path = os.path.join(bundle_dir, logo_base)
else:
    logo_path = logo_base