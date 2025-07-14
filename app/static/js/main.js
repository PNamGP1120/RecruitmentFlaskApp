document.addEventListener("DOMContentLoaded", function() {
    const urlParams = new URLSearchParams(window.location.search);
    const currentPage = urlParams.get('page') || '1';
    let item = document.getElementById(`page${currentPage}`);
    console.info(item);
    item.classList.add('active');
  });
