from flask import Flask, render_template_string, request, send_file, jsonify, redirect
from PIL import Image, ImageDraw, ImageFont
import io
from urllib.parse import urlencode
import json
import os

app = Flask(__name__)

# Settings file path
SETTINGS_FILE = 'printer_settings.json'

def load_settings():
    """Load printer settings from file"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    if os.path.exists("/app/" +SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {'printer_ip': '', 'printer_model': ''}

def is_printer_configured():
    """Check if printer is properly configured"""
    settings = load_settings()
    return bool(settings.get('printer_ip', '').strip())

def save_settings(settings):
    """Save printer settings to file"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"Error saving settings: {e}")

HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>To-Do Label Printer</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * {
      box-sizing: border-box;
    }

    body {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      margin: 0;
      padding: 0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .container {
      max-width: 600px;
      width: 90%;
      margin: 20px auto;
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(10px);
      border-radius: 20px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
      padding: 40px 50px;
      position: relative;
      overflow: hidden;
    }

    .container::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: linear-gradient(90deg, #667eea, #764ba2);
    }

    .title {
      font-size: 2.5em;
      font-weight: 700;
      background: linear-gradient(135deg, #667eea, #764ba2);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin-bottom: 0.5em;
      letter-spacing: -0.5px;
      text-align: center;
      line-height: 1.2;
    }

    .description {
      font-size: 1.1em;
      color: #6b7280;
      margin-bottom: 2.5em;
      line-height: 1.6;
      text-align: center;
      font-weight: 400;
    }

    form {
      margin-bottom: 30px;
    }

    label {
      display: block;
      text-align: left;
      margin-bottom: 8px;
      color: #374151;
      font-size: 0.95em;
      font-weight: 600;
      margin-left: 0;
    }

    input[type="text"], textarea {
      width: 100%;
      padding: 16px 20px;
      font-size: 1em;
      border: 2px solid #e5e7eb;
      border-radius: 12px;
      margin-bottom: 20px;
      box-sizing: border-box;
      transition: all 0.3s ease;
      background: #fff;
      font-family: inherit;
    }

    input[type="text"]:focus, textarea:focus {
      outline: none;
      border-color: #667eea;
      box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
      transform: translateY(-1px);
    }

    textarea {
      resize: vertical;
      min-height: 80px;
      max-height: 150px;
      line-height: 1.5;
    }

    input[type="submit"] {
      background: linear-gradient(135deg, #667eea, #764ba2);
      color: #fff;
      border: none;
      padding: 16px 32px;
      border-radius: 12px;
      font-size: 1.1em;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
      box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
      margin-top: 10px;
      width: 100%;
    }

    input[type="submit"]:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }

    input[type="submit"]:active {
      transform: translateY(0);
    }

    .preview {
      margin-top: 40px;
      text-align: center;
      padding: 30px;
      background: rgba(255, 255, 255, 0.8);
      border-radius: 16px;
      box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    .preview h3 {
      color: #374151;
      font-size: 1.5em;
      margin-bottom: 20px;
      font-weight: 600;
    }

    img {
      border: 3px solid #e5e7eb;
      border-radius: 16px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
      max-width: 100%;
      background: #fff;
      padding: 12px;
      transition: transform 0.3s ease;
    }

    img:hover {
      transform: scale(1.02);
    }

    .back-link {
      display: inline-block;
      margin-top: 30px;
      color: #667eea;
      text-decoration: none;
      font-weight: 600;
      transition: color 0.3s ease;
    }

    .back-link:hover {
      color: #764ba2;
      text-decoration: underline;
    }

    .confirmation {
      text-align: center;
      font-size: 1.2em;
      color: #059669;
      margin-top: 2em;
      font-weight: 500;
    }

    /* Toast styles */
    .toast {
      position: fixed;
      right: 30px;
      bottom: 30px;
      background: linear-gradient(135deg, #10b981, #059669);
      color: #fff;
      padding: 16px 24px;
      border-radius: 12px;
      box-shadow: 0 10px 30px rgba(16, 185, 129, 0.3);
      opacity: 0;
      transform: translateY(20px) scale(0.9);
      transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
      z-index: 9999;
      pointer-events: none;
      font-size: 1em;
      font-weight: 500;
      max-width: 300px;
    }

    .toast.show {
      opacity: 1;
      transform: translateY(0) scale(1);
    }

    .toast.error {
      background: linear-gradient(135deg, #ef4444, #dc2626);
      box-shadow: 0 10px 30px rgba(239, 68, 68, 0.3);
    }

    /* Responsive design */
    @media (max-width: 768px) {
      .container {
        padding: 30px 25px;
        margin: 10px;
        width: calc(100% - 20px);
      }

      .title {
        font-size: 2em;
      }

      .description {
        font-size: 1em;
      }

      input[type="text"], textarea {
        padding: 14px 16px;
        font-size: 0.95em;
      }

      input[type="submit"] {
        padding: 14px 24px;
        font-size: 1em;
      }

      .preview {
        padding: 20px;
      }

      .toast {
        right: 15px;
        bottom: 15px;
        max-width: calc(100vw - 30px);
      }
    }

    @media (max-width: 480px) {
      .container {
        padding: 20px 15px;
      }

      .title {
        font-size: 1.8em;
      }

      input[type="submit"] {
        font-size: 0.95em;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="title">To-Do Label Printer</div>
    <div style="text-align: right; margin-bottom: 20px;">
      <a href="/settings" class="back-link" style="font-size: 0.9em;">⚙️ Settings</a>
    </div>
    <form id="mainForm" method="post" enctype="multipart/form-data">
      <label for="label_title">Label Title</label>
      <input type="text" name="label_title" id="label_title" value="{{ label_title|default('') }}" placeholder="Label Title">
      <label for="label_description">Label Description</label>
      <input type="text" name="label_description" id="label_description" value="{{ label_description|default('') }}" placeholder="Label Description">
      <label for="task">To-Do Item</label>
      <textarea name="task" id="task" required placeholder="To-Do Item">{{ task|default('') }}</textarea>
      <input type="submit" value="Generate Label">
    </form>
    {% if image_url %}
      <div class="preview">
        <h3>Preview:</h3>
        <img src="{{ image_url }}" alt="Label Preview"/>
        <form id="printForm" method="post" action="/print">
          <input type="hidden" name="task" value="{{ task }}">
          <input type="hidden" name="label_title" value="{{ label_title }}">
          <input type="hidden" name="label_description" value="{{ label_description }}">
          <input type="submit" value="Print Label">
        </form>
      </div>
    {% endif %}
  </div>

  <div id="toast" class="toast" role="status" aria-live="polite"></div>

  <script>
    (function() {
      function showToast(message) {
        const toast = document.getElementById('toast');
        if (!toast) return;
        toast.textContent = message || 'Done';
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3000);
      }

      function attachPrintHandler() {
        const printForm = document.getElementById('printForm');
        if (!printForm) return;
        const submitBtn = printForm.querySelector('input[type="submit"]');

        printForm.addEventListener('submit', async function(e) {
          e.preventDefault();
          if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.value = 'Printing...';
          }
          try {
            const formData = new FormData(printForm);
            const res = await fetch('/print', { method: 'POST', body: formData });
            if (!res.ok) throw new Error('Request failed');
            const data = await res.json().catch(() => ({}));
            showToast((data && data.message) || 'Label sent to printer');

            // Reset the main form fields and explicitly clear inputs
            const mainForm = document.getElementById('mainForm');
            if (mainForm) {
              mainForm.reset(); // resets to initial values at page load
              const titleEl = document.getElementById('label_title');
              const descEl = document.getElementById('label_description');
              const taskEl = document.getElementById('task');
              if (titleEl) titleEl.value = '';
              if (descEl) descEl.value = '';
              if (taskEl) taskEl.value = '';
            }
            // Remove preview section
            const preview = document.querySelector('.preview');
            if (preview && preview.parentNode) {
              preview.parentNode.removeChild(preview);
            }
            // Clear URL query parameters so refresh doesn't restore old values
            window.history.replaceState(null, null, window.location.pathname);
          } catch (err) {
            console.error(err);
            showToast('Failed to print label');
          } finally {
            if (submitBtn) {
              submitBtn.disabled = false;
              submitBtn.value = 'Print Label';
            }
          }
        }, { once: true });
      }

      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', attachPrintHandler);
      } else {
        attachPrintHandler();
      }
    })();
  </script>
</body>
</html>
"""

SETTINGS_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Printer Settings - To-Do Label Printer</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * {
      box-sizing: border-box;
    }

    body {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      margin: 0;
      padding: 0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .container {
      max-width: 500px;
      width: 90%;
      margin: 20px auto;
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(10px);
      border-radius: 20px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
      padding: 40px 50px;
      position: relative;
      overflow: hidden;
    }

    .container::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: linear-gradient(90deg, #667eea, #764ba2);
    }

    .title {
      font-size: 2.2em;
      font-weight: 700;
      background: linear-gradient(135deg, #667eea, #764ba2);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin-bottom: 0.5em;
      letter-spacing: -0.5px;
      text-align: center;
      line-height: 1.2;
    }

    .description {
      font-size: 1em;
      color: #6b7280;
      margin-bottom: 2.5em;
      line-height: 1.6;
      text-align: center;
      font-weight: 400;
    }

    form {
      margin-bottom: 30px;
    }

    label {
      display: block;
      text-align: left;
      margin-bottom: 8px;
      color: #374151;
      font-size: 0.95em;
      font-weight: 600;
      margin-left: 0;
    }

    input[type="text"] {
      width: 100%;
      padding: 16px 20px;
      font-size: 1em;
      border: 2px solid #e5e7eb;
      border-radius: 12px;
      margin-bottom: 20px;
      box-sizing: border-box;
      transition: all 0.3s ease;
      background: #fff;
      font-family: inherit;
    }

    input[type="text"]:focus {
      outline: none;
      border-color: #667eea;
      box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
      transform: translateY(-1px);
    }

    input[type="submit"] {
      background: linear-gradient(135deg, #667eea, #764ba2);
      color: #fff;
      border: none;
      padding: 16px 32px;
      border-radius: 12px;
      font-size: 1.1em;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
      box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
      margin-top: 10px;
      width: 100%;
    }

    input[type="submit"]:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }

    .back-link {
      display: inline-block;
      margin-top: 30px;
      color: #667eea;
      text-decoration: none;
      font-weight: 600;
      transition: color 0.3s ease;
    }

    .back-link:hover {
      color: #764ba2;
      text-decoration: underline;
    }

    .success {
      text-align: center;
      font-size: 1.1em;
      color: #059669;
      margin-top: 2em;
      font-weight: 500;
    }

    .current-settings {
      background: rgba(255, 255, 255, 0.8);
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 30px;
      border: 1px solid #e5e7eb;
    }

    .current-settings h3 {
      color: #374151;
      margin-bottom: 15px;
      font-size: 1.2em;
    }

    .setting-item {
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;
      font-size: 0.95em;
    }

    .setting-label {
      font-weight: 600;
      color: #6b7280;
    }

    .setting-value {
      color: #374151;
      font-family: monospace;
      background: #f8fafc;
      padding: 2px 6px;
      border-radius: 4px;
    }

    /* Responsive design */
    @media (max-width: 768px) {
      .container {
        padding: 30px 25px;
        margin: 10px;
        width: calc(100% - 20px);
      }

      .title {
        font-size: 1.8em;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="title">Printer Settings</div>
    <div class="description">
      {% if not printer_ip %}
        Welcome! Please configure your Brother QL printer settings to get started.
      {% else %}
        Configure your Brother QL printer settings below.
      {% endif %}
    </div>

    {% if printer_ip %}
      <div class="current-settings">
        <h3>Current Settings</h3>
        <div class="setting-item">
          <span class="setting-label">Printer IP:</span>
          <span class="setting-value">{{ printer_ip }}</span>
        </div>
        <div class="setting-item">
          <span class="setting-label">Printer Model:</span>
          <span class="setting-value">{{ printer_model }}</span>
        </div>
      </div>
    {% endif %}

    <form method="post">
      <label for="printer_ip">Printer IP Address</label>
      <input type="text" name="printer_ip" id="printer_ip" value="{{ printer_ip }}" placeholder="192.168.1.100" required>

      <label for="printer_model">Printer Model</label>
      <input type="text" name="printer_model" id="printer_model" value="{{ printer_model }}" placeholder="QL-810W" required>

      <input type="submit" value="Save Settings">
    </form>

    {% if saved %}
      <div class="success">
        Settings saved successfully!
      </div>
    {% endif %}

    <div style="text-align: center; margin-top: 30px;">
      <a href="/" class="back-link">← Back to Label Printer</a>
    </div>
  </div>
</body>
</html>
"""

def create_todo_image(
    text,
    width=696,
    font_path="DejaVuSans-Bold.ttf",
    font_size=42,
    padding=60,
    bg_color="#f8f9fa",
    item_color="#ffffff",
    border_color="#ff0000",
    text_color="#000000",
    label_title="To-Do",
    label_description="Your task for today"
):
    # Calculate title and description presence
    has_title = bool(label_title.strip()) if label_title is not None else False
    has_desc = bool(label_description.strip()) if label_description is not None else False
    # Calculate max text width
    max_text_width = width - 2 * padding

    # Function to wrap text into multiple lines
    def wrap_text(text, font, max_width):
        if not text:
            return []
    
        words = text.split()
        lines = []
        word_iterations = 0
    
        while words:
            line = ''
            inner_iterations = 0
            while words:
                inner_iterations += 1
                word_iterations += 1
    
                # Safety check to prevent infinite loops
                if word_iterations > 1000:
                    lines.append(text[:50] + "..." if len(text) > 50 else text)
                    return lines
    
                test_line = f"{line} {words[0]}".strip()
    
                try:
                    bbox = font.getbbox(test_line)
                    w = bbox[2] - bbox[0]
    
                    if w <= max_width:
                        line = test_line
                        words.pop(0)
                    else:
                        break
                except Exception as e:
                    break
    
            if line:
                lines.append(line)
            else:
                # If we can't fit even the first word, add it anyway
                if words:
                    lines.append(words.pop(0))
    
        return lines

    # Wrap task text
    temp_font = ImageFont.truetype(font_path, font_size)
    task_lines = wrap_text(text, temp_font, max_text_width)

    # Ensure minimum height of 2 inches (600 pixels at 300 DPI)
    min_height = 600
    img_height = max(min_height, 600)  # Start with minimum height

    # Flexible layout: title can expand up to 1 inch (300 pixels at 300 DPI)
    max_title_height = min(300, (img_height - 2 * padding) // 2)  # Max 1 inch or half the label
    min_title_height = 60  # Minimum reasonable title space

    # Calculate content requirements including width constraints
    has_title = bool(label_title.strip()) if label_title is not None else False
    has_desc = bool(label_description.strip()) if label_description is not None else False


    # Available width for text
    available_text_width = width - 2 * padding

    # Test different font sizes to find optimal scaling
    def find_optimal_font_size(text, base_size, max_width):
        if not text:
            return base_size

        # Try different scale factors
        for scale in [2.0, 1.5, 1.2, 1.0, 0.9, 0.8, 0.7, 0.6, 0.5]:
            test_size = int(base_size * scale)
            test_font = ImageFont.truetype(font_path, test_size)
            bbox = test_font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            if text_width <= max_width:
                return test_size

        return int(base_size * 0.5)  # Minimum fallback

    # Find optimal font sizes for each text element with word wrapping
    def find_optimal_font_size_with_wrap(text, base_size, max_width):
        if not text:
            return base_size
    
        # Try different font sizes, using word wrapping to check if text fits
        start_size = base_size * 2
        end_size = base_size // 2
        step = -4  # Larger step to reduce iterations
    
        iteration_count = 0
    
        for test_size in range(start_size, end_size, step):  # From large to small
            iteration_count += 1
    
            # Safety check to prevent too many iterations
            if iteration_count > 10:  # Reduced from 20
                return base_size
    
            try:
                test_font = ImageFont.truetype(font_path, test_size)
                wrapped_lines = wrap_text(text, test_font, max_width)
    
                line_height = test_font.getbbox('Ay')[3] - test_font.getbbox('Ay')[1]
                total_height = line_height * len(wrapped_lines)
    
                # Check if it fits in reasonable space (not too many lines)
                if len(wrapped_lines) <= 3:  # Allow up to 3 lines
                    return test_size
    
            except Exception as e:
                continue
    
        return base_size  # Use base size instead of half size

    title_font_size = find_optimal_font_size_with_wrap(label_title, 48, available_text_width) if has_title else 0
    desc_font_size = find_optimal_font_size_with_wrap(label_description, 36, available_text_width) if has_desc else 0

    # Task font size (already handles wrapping)
    task_font_size = 36
    temp_task_font = ImageFont.truetype(font_path, task_font_size)
    max_task_width = 0
    for line in task_lines:
        bbox = temp_task_font.getbbox(line)
        line_width = bbox[2] - bbox[0]
        max_task_width = max(max_task_width, line_width)

    if max_task_width > available_text_width:
        task_font_size = find_optimal_font_size("Sample task text", 36, available_text_width)

    # Create fonts with optimal sizes
    font_title = ImageFont.truetype(font_path, title_font_size) if has_title else None
    font_desc = ImageFont.truetype(font_path, desc_font_size) if has_desc else None
    font_task = ImageFont.truetype(font_path, task_font_size)

    # Wrap text with final fonts
    title_lines = wrap_text(label_title, font_title, available_text_width) if has_title else []
    desc_lines = wrap_text(label_description, font_desc, available_text_width) if has_desc else []

    # Calculate actual heights with scaled fonts and wrapped text
    title_height = 0
    if has_title and title_lines:
        line_height = font_title.getbbox('Ay')[3] - font_title.getbbox('Ay')[1]
        title_height = line_height * len(title_lines)

    desc_height = 0
    if has_desc and desc_lines:
        line_height = font_desc.getbbox('Ay')[3] - font_desc.getbbox('Ay')[1]
        desc_height = line_height * len(desc_lines)

    line_height = font_task.getbbox('Ay')[3] - font_task.getbbox('Ay')[1]
    task_height = line_height * len(task_lines)

    # Dynamic space allocation
    total_available_height = img_height - 2 * padding
    min_content_height = 100  # Minimum space for content area

    # Calculate required title space (with max limit)
    actual_title_height = min(title_height, max_title_height) if has_title else 0

    # Ensure title gets at least its required space but not more than max
    if has_title and title_height > min_title_height:
        actual_title_height = min(title_height, max_title_height)

    # Calculate remaining space for content
    remaining_height = total_available_height - actual_title_height
    if remaining_height < min_content_height:
        # Need to expand image or reduce title space
        if actual_title_height > min_title_height:
            # Reduce title space to fit minimum content area
            actual_title_height = total_available_height - min_content_height
            actual_title_height = max(actual_title_height, min_title_height)
            remaining_height = min_content_height
        else:
            # Expand image height
            extra_height = min_content_height - remaining_height
            img_height += extra_height
            remaining_height = min_content_height

    # Allocate space for content sections
    content_height_needed = 0
    if has_desc:
        content_height_needed += desc_height + 12  # gap
    content_height_needed += task_height

    # If content needs more space, expand image
    if content_height_needed > remaining_height:
        extra_height = content_height_needed - remaining_height
        img_height += extra_height
        remaining_height = content_height_needed

    # Final area assignments
    title_area_height = actual_title_height
    content_area_height = remaining_height

    # Create image with subtle gradient background
    img = Image.new("RGB", (width, img_height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Draw main rounded rectangle with enhanced styling
    rect_radius = 32
    margin = 16
    rect_x0, rect_y0 = margin, margin
    rect_x1, rect_y1 = width - margin, img_height - margin

    # Draw shadow effect
    shadow_offset = 4
    shadow_color = (0, 0, 0, 30)  # Semi-transparent black
    shadow_rect = [rect_x0 + shadow_offset, rect_y0 + shadow_offset, rect_x1 + shadow_offset, rect_y1 + shadow_offset]
    # Note: PIL doesn't support alpha in RGB mode, so we'll use a solid shadow color
    shadow_color_solid = (240, 240, 240)  # Light gray shadow
    draw.rounded_rectangle(shadow_rect, radius=rect_radius, fill=shadow_color_solid)

    # Draw main rectangle
    draw.rounded_rectangle(
        [rect_x0, rect_y0, rect_x1, rect_y1],
        radius=rect_radius,
        fill=item_color,
        outline=border_color,
        width=3
    )

    # Add decorative border lines
    inner_margin = 8
    inner_rect = [rect_x0 + inner_margin, rect_y0 + inner_margin, rect_x1 - inner_margin, rect_y1 - inner_margin]
    draw.rounded_rectangle(inner_rect, radius=rect_radius - 8, outline=border_color, width=1)

    # Visual separator between title and content areas removed for cleaner look

    # Draw sections in proportional layout with wrapped text
    # Title area: top 1/3
    if has_title and title_lines:
        title_y = rect_y0 + padding // 2
        # Center title block in its area
        title_block_height = title_height
        title_center_y = title_y + (title_area_height - title_block_height) // 2

        # Draw title lines
        current_y = title_center_y
        for line in title_lines:
            draw.text(
                (rect_x0 + padding // 2, current_y),
                line,
                font=font_title,
                fill="#cc0000"  # Slightly darker red for better contrast
            )
            current_y += font_title.getbbox('Ay')[3] - font_title.getbbox('Ay')[1]

    # Content area: bottom 2/3 with spacing from title
    content_start_y = rect_y0 + padding // 2 + title_area_height
    # Add extra space between title and content areas
    content_spacing = 20  # pixels of space between title and description
    content_y = content_start_y + content_spacing

    if has_desc and desc_lines:
        # Draw description lines
        for line in desc_lines:
            draw.text(
                (rect_x0 + padding // 2, content_y),
                line,
                font=font_desc,
                fill="#333333"  # Darker gray for better readability
            )
            content_y += font_desc.getbbox('Ay')[3] - font_desc.getbbox('Ay')[1]
        content_y += 12  # gap after description

    # Draw task lines
    for line in task_lines:
        draw.text(
            (rect_x0 + padding // 2, content_y),
            line,
            font=font_task,
            fill="#000000"  # Pure black for task text
        )
        content_y += line_height

    return img

@app.route('/', methods=['GET', 'POST'])
def index():
    # Check if printer is configured
    if not is_printer_configured():
        return redirect('/settings')

    image_url = None
    task = request.args.get('task', '')
    label_title = request.args.get('label_title', '')
    label_description = request.args.get('label_description', '')

    if request.method == 'POST':
        task = request.form['task']
        label_title = request.form['label_title']
        label_description = request.form['label_description']
        # Redirect to GET with query params to prevent form resubmission warning
        return redirect(f'/?{urlencode({"task": task, "label_title": label_title, "label_description": label_description})}')

    # Generate preview URL if we have task data
    if task:
        params = urlencode({"task": task, "label_title": label_title, "label_description": label_description})
        image_url = f"/label.png?{params}"

    return render_template_string(
        HTML,
        image_url=image_url,
        task=task,
        label_title=label_title,
        label_description=label_description
    )

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    settings_data = load_settings()
    saved = False

    if request.method == 'POST':
        settings_data['printer_ip'] = request.form['printer_ip']
        settings_data['printer_model'] = request.form['printer_model']
        save_settings(settings_data)
        saved = True

    return render_template_string(
        SETTINGS_HTML,
        printer_ip=settings_data['printer_ip'],
        printer_model=settings_data['printer_model'],
        saved=saved
    )

@app.route('/label.png')
def label_png():
    task = request.args.get('task', '')
    label_title = request.args.get('label_title', '')
    label_description = request.args.get('label_description', '')

    try:
        img = create_todo_image(
            task,
            label_title=label_title,
            label_description=label_description
        )
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return send_file(buf, mimetype='image/png')
    except Exception as e:
        # Return a simple error image
        error_img = Image.new('RGB', (400, 200), color='red')
        draw = ImageDraw.Draw(error_img)
        draw.text((10, 10), f"Error: {str(e)}", fill='white')
        buf = io.BytesIO()
        error_img.save(buf, format='PNG')
        buf.seek(0)
        return send_file(buf, mimetype='image/png')

@app.route('/print', methods=['POST'])
def print_label():
    try:
        task = request.form['task']
        label_title = request.form.get('label_title', '')
        label_description = request.form.get('label_description', '')

        # Load and validate printer settings
        settings_data = load_settings()
        if not settings_data.get('printer_ip', '').strip():
            return jsonify({"status": "error", "message": "Printer not configured. Please go to Settings to configure your printer."}), 400

        if not settings_data.get('printer_model', '').strip():
            return jsonify({"status": "error", "message": "Printer model not configured. Please go to Settings to configure your printer."}), 400

        img = create_todo_image(
            task,
            label_title=label_title,
            label_description=label_description
        )
        img.save("label_to_print.png")

        # Add your brother_ql print code here if desired
        from brother_ql.backends.helpers import send
        from brother_ql.conversion import convert
        from brother_ql.raster import BrotherQLRaster

        # Create the raster object
        qlr = BrotherQLRaster(settings_data['printer_model'])
        qlr.exception_on_warning = True

        # Convert the image to printer instructions
        instructions = convert(
            qlr=qlr,
            images=["label_to_print.png"],
            label='62',
            rotate='auto',  # or 0, 90, 180, 270
            threshold=70.0,  # Adjust if needed
            dither=True,
            compress=True,
            red=True,  # For two-color printers
            dpi_600=False,
            hq=True,
            cut=True
        )

        # Send to printer using configured IP
        send(
            instructions=instructions,
            printer_identifier=f"tcp://{settings_data['printer_ip']}",
            backend_identifier="network",
            blocking=True
        )
        return jsonify({"status": "ok", "message": "Your label has been sent to the printer."})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Print failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
