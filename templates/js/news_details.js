// JavaScript ?????? ????? ??????

function showArticleDetails(articleId) {
    // ???? ?????? ??????? ????? ????? ??? ???????
    console.log("??? ?????? ??????:", articleId);

    // ????? ??? ????? ????? ???????? ??? ???? ???????? ?? ??? ????? ??????
    alert("???? ??? ?????? ?????? ID: " + articleId);
}

// ????? ??????? ????????
document.addEventListener("DOMContentLoaded", () => {
    const cards = document.querySelectorAll('.news-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
});