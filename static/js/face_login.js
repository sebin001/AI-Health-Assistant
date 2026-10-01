document.addEventListener("DOMContentLoaded", function () {

    const faceLoginBtn =
        document.getElementById("faceLoginBtn");

    const modal =
        document.getElementById("faceLoginModal");

    const video =
        document.getElementById("faceLoginCamera");

    const status =
        document.getElementById("faceLoginStatus");

    const cancelBtn =
        document.getElementById("faceLoginCancel");

    const retryBtn =
        document.getElementById("faceLoginRetry");

    const config =
        document.getElementById("faceLoginConfig");

    const loginUrl =
        config.dataset.loginUrl;

    let stream = null;
    let scanTimer = null;
    let isScanning = false;


    // =====================================================
    // CSRF
    // =====================================================

    function getCookie(name) {

        const cookies =
            document.cookie.split(";");

        for (let cookie of cookies) {

            cookie = cookie.trim();

            if (
                cookie.startsWith(name + "=")
            ) {
                return decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
            }
        }

        return null;
    }


    // =====================================================
    // STATUS
    // =====================================================

    function setStatus(
        message,
        type = ""
    ) {

        status.textContent = message;

        status.className =
            "face-login-status";

        if (type) {
            status.classList.add(type);
        }
    }


    // =====================================================
    // START CAMERA
    // =====================================================

    async function startCamera() {

        stopCamera();

        setStatus(
            "Starting camera...",
            "loading"
        );

        try {

            stream =
                await navigator.mediaDevices.getUserMedia(
                    {
                        video: {
                            facingMode: "user",
                            width: {
                                ideal: 640
                            },
                            height: {
                                ideal: 480
                            }
                        },
                        audio: false
                    }
                );

            video.srcObject = stream;

            await video.play();

            setStatus(
                "Camera ready. Look directly at the camera.",
                "loading"
            );

            startScanning();

        } catch (error) {

            console.error(
                "Camera error:",
                error
            );

            setStatus(
                "Unable to access camera. Please allow camera permission and try again.",
                "error"
            );
        }
    }


    // =====================================================
    // STOP CAMERA
    // =====================================================

    function stopCamera() {

        if (scanTimer) {

            clearInterval(scanTimer);

            scanTimer = null;
        }

        isScanning = false;

        if (stream) {

            stream.getTracks().forEach(
                track => track.stop()
            );

            stream = null;
        }

        if (video) {
            video.srcObject = null;
        }
    }


    // =====================================================
    // CAPTURE IMAGE
    // =====================================================

    function captureImage() {

        if (
            !video.videoWidth ||
            !video.videoHeight
        ) {
            return null;
        }

        const canvas =
            document.createElement("canvas");

        canvas.width =
            video.videoWidth;

        canvas.height =
            video.videoHeight;

        const context =
            canvas.getContext("2d");

        context.drawImage(
            video,
            0,
            0,
            canvas.width,
            canvas.height
        );

        return canvas.toDataURL(
            "image/jpeg",
            0.90
        );
    }


    // =====================================================
    // START SCANNING
    // =====================================================

    function startScanning() {

        if (scanTimer) {
            clearInterval(scanTimer);
        }

        scanTimer =
            setInterval(
                scanFace,
                1200
            );
    }


    // =====================================================
    // SEND FACE TO SERVER
    // =====================================================

    async function scanFace() {

        if (
            isScanning ||
            !stream
        ) {
            return;
        }

        const image =
            captureImage();

        if (!image) {
            return;
        }

        isScanning = true;

        setStatus(
            "Verifying your Face ID...",
            "loading"
        );

        const formData =
            new FormData();

        formData.append(
            "image",
            image
        );

        try {

            const response =
                await fetch(
                    loginUrl,
                    {
                        method: "POST",

                        headers: {
                            "X-CSRFToken":
                                getCookie("csrftoken")
                        },

                        body: formData
                    }
                );

            const data =
                await response.json();


            if (data.success) {

                setStatus(
                    "Face ID verified successfully. Logging you in...",
                    "success"
                );

                stopCamera();

                setTimeout(
                    function () {

                        window.location.href =
                            data.redirect ||
                            "/dashboard/";

                    },
                    1000
                );

            } else {

                setStatus(
                    data.message ||
                    "Face not recognized. Please try again.",
                    "error"
                );

                isScanning = false;
            }

        } catch (error) {

            console.error(
                "Face login error:",
                error
            );

            setStatus(
                "Unable to connect to the Face ID service.",
                "error"
            );

            isScanning = false;
        }
    }


    // =====================================================
    // OPEN MODAL
    // =====================================================

    faceLoginBtn.addEventListener(
        "click",
        function () {

            modal.classList.add(
                "active"
            );

            startCamera();
        }
    );


    // =====================================================
    // CANCEL
    // =====================================================

    cancelBtn.addEventListener(
        "click",
        function () {

            stopCamera();

            modal.classList.remove(
                "active"
            );

            setStatus(
                "Starting camera..."
            );
        }
    );


    // =====================================================
    // RETRY
    // =====================================================

    retryBtn.addEventListener(
        "click",
        function () {

            startCamera();
        }
    );


    // =====================================================
    // CLICK OUTSIDE MODAL
    // =====================================================

    modal.addEventListener(
        "click",
        function (event) {

            if (
                event.target === modal
            ) {

                stopCamera();

                modal.classList.remove(
                    "active"
                );
            }
        }
    );


    // =====================================================
    // CLEANUP
    // =====================================================

    window.addEventListener(
        "beforeunload",
        function () {

            stopCamera();
        }
    );

});