document.addEventListener("DOMContentLoaded", function () {
    const hintButton = document.getElementById("hint-button");
    const hintText = document.getElementById("hint-text");

    if (hintButton && hintText) {
        let hintsUsed = 0; // Счетчик использованных подсказок
        const hints = [
            "Первая буква 'х'",
            "В слове 8 букв",
            "В этом слове есть буквы 'æ', 'дж'"
        ];

        hintButton.addEventListener("click", function () {
            if (hintsUsed < hints.length) {
                hintText.textContent = hints[hintsUsed];
                hintsUsed++;
            } else {
                alert("Вы использовали все подсказки!");
            }
        });
    }
});