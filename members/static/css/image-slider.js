let slideIndex = 0;
showSlides();
function plusSlides(n) {
showSlides(slideIndex += n);
}

function showSlides() {
    let slides = document.getElementsByClassName("myslides");
    for (let i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }
    slideIndex++;
    if (slideIndex > slides.length) {
        slideIndex = 1;
    }
    slides[slideIndex - 1].style.display = "grid";
    setTimeout(showSlides, 5000); // Change slide every 3 seconds
}
