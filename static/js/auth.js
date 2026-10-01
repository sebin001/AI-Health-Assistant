function togglePassword(inputId, button) {

    const input =
        document.getElementById(inputId);

    if (!input || !button) {
        return;
    }


    const icon =
        button.querySelector("i");


    if (input.type === "password") {

        input.type = "text";


        if (icon) {

            icon.classList.remove(
                "fa-eye"
            );

            icon.classList.add(
                "fa-eye-slash"
            );
        }


        button.setAttribute(
            "aria-label",
            "Hide password"
        );

    } else {

        input.type = "password";


        if (icon) {

            icon.classList.remove(
                "fa-eye-slash"
            );

            icon.classList.add(
                "fa-eye"
            );
        }


        button.setAttribute(
            "aria-label",
            "Show password"
        );
    }
}


/* ============================================================
   FACE LOGIN
   ============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const faceLoginBtn =
            document.getElementById(
                "faceLoginBtn"
            );


        if (faceLoginBtn) {

            faceLoginBtn.addEventListener(
                "click",
                function () {

                    alert(
                        "Face ID Login will be available in the next step."
                    );

                }
            );

        }

    }
);