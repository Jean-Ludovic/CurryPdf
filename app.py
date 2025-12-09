import streamlit as st
import qrcode
from PIL import Image
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import datetime

# Page configuration
st.set_page_config(
    page_title="QR Code Generator & PDF Exporter",
    page_icon="📱",
    layout="centered"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .stTextArea textarea {
        min-height: 150px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">📱 QR Code Generator & PDF Exporter</h1>', unsafe_allow_html=True)

# Initialize session state
if 'qr_image' not in st.session_state:
    st.session_state.qr_image = None
if 'link' not in st.session_state:
    st.session_state.link = ""
if 'text_content' not in st.session_state:
    st.session_state.text_content = ""

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    # QR Code size
    qr_size = st.slider("QR Code Size", min_value=100, max_value=500, value=300, step=50)
    
    # QR Code border
    border = st.slider("QR Code Border", min_value=1, max_value=10, value=4, step=1)
    
    # Error correction level
    error_correction = st.selectbox(
        "Error Correction Level",
        ["LOW", "MEDIUM", "QUARTILE", "HIGH"],
        index=1
    )
    
    error_correction_map = {
        "LOW": qrcode.constants.ERROR_CORRECT_L,
        "MEDIUM": qrcode.constants.ERROR_CORRECT_M,
        "QUARTILE": qrcode.constants.ERROR_CORRECT_Q,
        "HIGH": qrcode.constants.ERROR_CORRECT_H
    }

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🔗 Enter Link")
    link_input = st.text_input(
        "URL/Link",
        value=st.session_state.link,
        placeholder="https://example.com",
        key="link_input"
    )
    
    if st.button("Generate QR Code", type="primary", use_container_width=True):
        if link_input.strip():
            try:
                # Create QR code
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=error_correction_map[error_correction],
                    box_size=10,
                    border=border,
                )
                qr.add_data(link_input)
                qr.make(fit=True)
                
                # Create image
                img = qr.make_image(fill_color="black", back_color="white")
                img = img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
                
                # Store in session state
                st.session_state.qr_image = img
                st.session_state.link = link_input
                st.success("QR Code generated successfully!")
            except Exception as e:
                st.error(f"Error generating QR code: {str(e)}")
        else:
            st.warning("Please enter a valid link!")

with col2:
    st.subheader("📝 Add/Edit Text")
    text_content = st.text_area(
        "Text Content",
        value=st.session_state.text_content,
        placeholder="Enter your text here...\nYou can add multiple lines.\nThis text will appear in the PDF.",
        height=200,
        key="text_input"
    )
    st.session_state.text_content = text_content

# Display QR Code
if st.session_state.qr_image:
    st.divider()
    st.subheader("📱 Generated QR Code")
    
    # Display QR code
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(st.session_state.qr_image, caption=f"QR Code for: {st.session_state.link}")
    
    # Download and PDF buttons
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        # Download QR Code as PNG
        img_buffer = io.BytesIO()
        st.session_state.qr_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        st.download_button(
            label="📥 Download QR Code (PNG)",
            data=img_buffer,
            file_name=f"qrcode_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            mime="image/png",
            use_container_width=True
        )
    
    with col2:
        # Download QR Code as JPG
        img_buffer_jpg = io.BytesIO()
        rgb_image = st.session_state.qr_image.convert('RGB')
        rgb_image.save(img_buffer_jpg, format='JPEG', quality=95)
        img_buffer_jpg.seek(0)
        
        st.download_button(
            label="📥 Download QR Code (JPG)",
            data=img_buffer_jpg,
            file_name=f"qrcode_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
            mime="image/jpeg",
            use_container_width=True
        )
    
    with col3:
        # Generate and download PDF
        def generate_pdf():
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            
            # Title
            c.setFont("Helvetica-Bold", 20)
            c.drawString(50, height - 50, "QR Code Document")
            
            # Date
            c.setFont("Helvetica", 10)
            date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.drawString(50, height - 75, f"Generated on: {date_str}")
            
            # Link
            c.setFont("Helvetica", 12)
            c.drawString(50, height - 100, f"Link: {st.session_state.link}")
            
            # Text content
            if st.session_state.text_content.strip():
                y_position = height - 130
                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, y_position, "Additional Text:")
                y_position -= 20
                
                c.setFont("Helvetica", 11)
                # Handle multi-line text
                lines = st.session_state.text_content.split('\n')
                for line in lines:
                    # Word wrap for long lines
                    words = line.split(' ')
                    current_line = ""
                    for word in words:
                        test_line = current_line + word + " " if current_line else word + " "
                        if c.stringWidth(test_line, "Helvetica", 11) < width - 100:
                            current_line = test_line
                        else:
                            if current_line:
                                c.drawString(50, y_position, current_line.strip())
                                y_position -= 15
                            current_line = word + " "
                    if current_line:
                        c.drawString(50, y_position, current_line.strip())
                        y_position -= 15
                    y_position -= 5  # Extra space between paragraphs
                    
                    if y_position < 200:  # Start new page if needed
                        c.showPage()
                        y_position = height - 50
            
            # QR Code image
            qr_y_position = y_position - 50 if st.session_state.text_content.strip() else height - 200
            qr_size_pdf = min(200, qr_y_position - 100)
            
            # Convert PIL image to format reportlab can use
            img_buffer_pdf = io.BytesIO()
            st.session_state.qr_image.save(img_buffer_pdf, format='PNG')
            img_buffer_pdf.seek(0)
            qr_img = ImageReader(img_buffer_pdf)
            
            # Center the QR code
            qr_x = (width - qr_size_pdf) / 2
            c.drawImage(qr_img, qr_x, qr_y_position - qr_size_pdf, 
                       width=qr_size_pdf, height=qr_size_pdf)
            
            c.save()
            buffer.seek(0)
            return buffer
        
        pdf_buffer = generate_pdf()
        st.download_button(
            label="📄 Download as PDF",
            data=pdf_buffer,
            file_name=f"qrcode_document_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>QR Code Generator & PDF Exporter | Created with Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)

