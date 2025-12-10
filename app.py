import streamlit as st
import qrcode
from PIL import Image
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import datetime

# Page configuration
st.set_page_config(
    page_title="QR Code Generator & PDF Exporter",
    page_icon="📱",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">📱 QR Code Generator & PDF Exporter</h1>', unsafe_allow_html=True)

# Sidebar for QR Code settings
with st.sidebar:
    st.header("⚙️ QR Code Settings")
    qr_size = st.slider("QR Code Size", 100, 500, 300, 50)
    border = st.slider("QR Code Border", 1, 10, 4)
    error_correction = st.selectbox(
        "Error Correction",
        ["LOW", "MEDIUM", "QUARTILE", "HIGH"],
        index=1
    )
    
    error_map = {
        "LOW": qrcode.constants.ERROR_CORRECT_L,
        "MEDIUM": qrcode.constants.ERROR_CORRECT_M,
        "QUARTILE": qrcode.constants.ERROR_CORRECT_Q,
        "HIGH": qrcode.constants.ERROR_CORRECT_H
    }

# Main layout with tabs
tab1, tab2 = st.tabs(["📝 Content", "🎨 Formatting"])

with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🔗 Enter Link")
        link = st.text_input("URL/Link", placeholder="https://example.com", key="link")
    
    with col2:
        st.subheader("📝 Add Text")
        text = st.text_area(
            "Text Content",
            placeholder="Enter your text here...",
            height=120,
            key="text"
        )

with tab2:
    st.subheader("🎨 Text Formatting Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Title Formatting**")
        title_font = st.selectbox(
            "Title Font",
            ["Helvetica", "Helvetica-Bold", "Times-Roman", "Times-Bold", "Courier", "Courier-Bold"],
            index=1
        )
        title_size = st.slider("Title Size", 12, 36, 20)
        title_color = st.color_picker("Title Color", "#000000")
    
    with col2:
        st.markdown("**Text Formatting**")
        text_font = st.selectbox(
            "Text Font",
            ["Helvetica", "Helvetica-Bold", "Times-Roman", "Times-Bold", "Courier", "Courier-Bold"],
            index=0
        )
        text_size = st.slider("Text Size", 8, 24, 11)
        text_color = st.color_picker("Text Color", "#000000")
    
    with col3:
        st.markdown("**Layout**")
        text_align = st.selectbox(
            "Text Alignment",
            ["Left", "Center", "Right"],
            index=0
        )
        line_spacing = st.slider("Line Spacing", 10, 30, 15)
        margin = st.slider("Page Margin", 30, 100, 50)

# Generate button
if st.button("🎯 Generate QR Code", type="primary", use_container_width=True):
    if link.strip():
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=error_map[error_correction],
                box_size=10,
                border=border,
            )
            qr.add_data(link)
            qr.make(fit=True)
            
            qr_image = qr.make_image(fill_color="black", back_color="white")
            qr_image = qr_image.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
            
            st.session_state.qr_image = qr_image
            st.session_state.link = link
            st.session_state.text = text
            st.success("✅ QR Code generated!")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    else:
        st.warning("⚠️ Please enter a valid link!")

# Display and download QR Code
if 'qr_image' in st.session_state and st.session_state.qr_image:
    st.divider()
    st.subheader("📱 Your QR Code")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(st.session_state.qr_image, caption=f"QR Code: {st.session_state.link}")
    
    st.divider()
    
    # Download buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # PNG download
        img_buf = io.BytesIO()
        st.session_state.qr_image.save(img_buf, format='PNG')
        img_buf.seek(0)
        
        st.download_button(
            "📥 Download PNG",
            img_buf,
            f"qrcode_{datetime.datetime.now():%Y%m%d_%H%M%S}.png",
            "image/png",
            use_container_width=True
        )
    
    with col2:
        # JPG download
        jpg_buf = io.BytesIO()
        st.session_state.qr_image.convert('RGB').save(jpg_buf, format='JPEG', quality=95)
        jpg_buf.seek(0)
        
        st.download_button(
            "📥 Download JPG",
            jpg_buf,
            f"qrcode_{datetime.datetime.now():%Y%m%d_%H%M%S}.jpg",
            "image/jpeg",
            use_container_width=True
        )
    
    with col3:
        # PDF generation with formatting
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))
        
        def create_pdf():
            buf = io.BytesIO()
            c = canvas.Canvas(buf, pagesize=A4)
            w, h = A4
            
            # Title
            c.setFont(title_font, title_size)
            c.setFillColorRGB(*hex_to_rgb(title_color))
            
            title_text = "QR Code Document"
            if text_align == "Center":
                title_x = (w - c.stringWidth(title_text, title_font, title_size)) / 2
            elif text_align == "Right":
                title_x = w - margin - c.stringWidth(title_text, title_font, title_size)
            else:
                title_x = margin
            
            c.drawString(title_x, h - margin, title_text)
            
            # Date and Link
            c.setFont("Helvetica", 10)
            c.setFillColorRGB(0, 0, 0)
            c.drawString(margin, h - margin - 25, f"Generated: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}")
            c.drawString(margin, h - margin - 40, f"Link: {st.session_state.link}")
            
            # Text content
            y_pos = h - margin - 70
            if st.session_state.text.strip():
                c.setFont(title_font, 14)
                section_title = "Additional Text:"
                
                if text_align == "Center":
                    section_x = (w - c.stringWidth(section_title, title_font, 14)) / 2
                elif text_align == "Right":
                    section_x = w - margin - c.stringWidth(section_title, title_font, 14)
                else:
                    section_x = margin
                
                c.drawString(section_x, y_pos, section_title)
                y_pos -= 25
                
                c.setFont(text_font, text_size)
                c.setFillColorRGB(*hex_to_rgb(text_color))
                
                for line in st.session_state.text.split('\n'):
                    words = line.split()
                    current = ""
                    for word in words:
                        test = f"{current} {word}".strip()
                        if c.stringWidth(test, text_font, text_size) < w - (2 * margin):
                            current = test
                        else:
                            if current:
                                if text_align == "Center":
                                    text_x = (w - c.stringWidth(current, text_font, text_size)) / 2
                                elif text_align == "Right":
                                    text_x = w - margin - c.stringWidth(current, text_font, text_size)
                                else:
                                    text_x = margin
                                
                                c.drawString(text_x, y_pos, current)
                                y_pos -= line_spacing
                            current = word
                    
                    if current:
                        if text_align == "Center":
                            text_x = (w - c.stringWidth(current, text_font, text_size)) / 2
                        elif text_align == "Right":
                            text_x = w - margin - c.stringWidth(current, text_font, text_size)
                        else:
                            text_x = margin
                        
                        c.drawString(text_x, y_pos, current)
                        y_pos -= line_spacing + 5
            
            # QR Code
            qr_y = y_pos - 50 if st.session_state.text.strip() else h - 200
            qr_pdf_size = min(250, max(150, qr_y - 100))
            
            img_buf = io.BytesIO()
            st.session_state.qr_image.save(img_buf, format='PNG')
            img_buf.seek(0)
            
            qr_x = (w - qr_pdf_size) / 2
            c.drawImage(ImageReader(img_buf), qr_x, qr_y - qr_pdf_size, 
                       qr_pdf_size, qr_pdf_size)
            
            c.save()
            buf.seek(0)
            return buf
        
        st.download_button(
            "📄 Download PDF",
            create_pdf(),
            f"qrcode_{datetime.datetime.now():%Y%m%d_%H%M%S}.pdf",
            "application/pdf",
            use_container_width=True
        )

# Footer
st.divider()
st.markdown(
    "<div style='text-align: center; color: #666; padding: 20px;'>"
    "<p>QR Code Generator & PDF Exporter | Built with Streamlit</p>"
    "</div>",
    unsafe_allow_html=True
)