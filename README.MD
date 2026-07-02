# sms2i-WebApp

<p align="center">
  <img src="static/readmeicon.jpg" alt="sms2i Icon" width="360" />
</p>
<p align="center">
<strong>Scan. Match. Count.</strong>
</p>

<p align="center">
  <a href="#about">About</a> •
  <a href="#features">Features</a> •
  <a href="#tech-stack">Tech Stack</a> •
  <a href="#getting-started">Getting Started</a>
</p>

---

## 📖 About
**sms2i-WebApp** is a simple web dashboard that uses your webcam to detect, count, and identify products in real time. It scans the shape of any item placed in front of the camera, matches it against blueprint pictures saved in your database, and instantly updates the product info on the web page.

## ✨ Features
* **Real-Time Camera Stream**: Watch the live video feed directly on your web dashboard.
* **Smart Shape Matching**: Automatically matches real-world objects with saved product blueprints in your database.
* **Live Control Sliders**: Tweak the object size limits, black-and-white thresholding, and processing speeds on the fly without restarting the server.
* **Product Manager**: Easily register new products with a reference code, name, and 3 product photos.
* **Instant HTML Updates**: The product name, reference, and total count change on your screen instantly using clean background updates.

## 🛠 Tech Stack
* **Frontend**: HTML5, CSS3, and Vanilla JavaScript.
* **Backend**: Flask (Python).
* **Vision Processing**: OpenCV and NumPy.
* **Database**: SQLite3 (`product.db`).

## 🚀 Getting Started

### Prerequisites
Make sure you have Python installed on your computer and a working webcam.

### Installation
1. Clone the repository:
```bash
git clone [https://github.com/galacticpsychopath/sms2i-WebApp.git](https://github.com/galacticpsychopath/sms2i-WebApp.git)
cd sms2i-WebApp