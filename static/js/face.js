document.addEventListener("DOMContentLoaded", function () {

    const video = document.getElementById("faceCamera");
    const canvas = document.getElementById("faceCanvas");

    const faceConfig = document.getElementById("faceConfig");

    const cameraStatus =
        document.getElementById("cameraStatus");

    const faceStatus =
        document.getElementById("faceStatus");

    const stopCameraBtn =
        document.getElementById("stopCameraBtn");

    const retryCameraBtn =
        document.getElementById("retryCameraBtn");


    // ========================================================
    // URLs
    // ========================================================

    if (!faceConfig) {
        console.error(
            "Face configuration element not found."
        );
        return;
    }

    const detectUrl =
        faceConfig.dataset.detectUrl;

    const saveUrl =
        faceConfig.dataset.saveUrl;


    // ========================================================
    // Variables
    // ========================================================

    let cameraStream = null;

    let scanTimer = null;

    let isProcessing = false;

    let faceRegistered = false;


    // ========================================================
    // CSRF TOKEN
    // ========================================================

    function getCookie(name) {

        let cookieValue = null;

        if (document.cookie && document.cookie !== "") {

            const cookies =
                document.cookie.split(";");

            for (let cookie of cookies) {

                cookie = cookie.trim();

                if (
                    cookie.substring(
                        0,
                        name.length + 1
                    ) === name + "="
                ) {

                    cookieValue =
                        decodeURIComponent(
                            cookie.substring(
                                name.length + 1
                            )
                        );

                    break;
                }
            }
        }

        return cookieValue;
    }


    // ========================================================
    // STATUS
    // ========================================================

    function setStatus(
        type,
        title,
        message,
        icon
    ) {

        if (!faceStatus) {
            return;
        }

        faceStatus.className =
            "face-status-box " + type;

        faceStatus.innerHTML = `

            <div class="face-status-icon">
                <i class="${icon}"></i>
            </div>

            <div class="face-status-text">

                <strong>
                    ${title}
                </strong>

                <span>
                    ${message}
                </span>

            </div>
        `;
    }


    // ========================================================
    // CAMERA STATUS
    // ========================================================

    function setCameraStatus(
        text,
        active = false
    ) {

        if (!cameraStatus) {
            return;
        }

        cameraStatus.innerHTML = `

            <span
                class="camera-status-dot ${
                    active ? "active" : ""
                }"
            ></span>

            ${text}
        `;
    }


    // ========================================================
    // START CAMERA
    // ========================================================

    async function startCamera() {

        stopCamera();

        faceRegistered = false;
        isProcessing = false;

        setStatus(
            "loading",
            "Starting camera",
            "Please allow camera access.",
            "fa-solid fa-camera"
        );

        setCameraStatus(
            "Starting camera..."
        );


        try {

            cameraStream =
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


            video.srcObject =
                cameraStream;


            await video.play();


            setCameraStatus(
                "Camera active",
                true
            );


            setStatus(
                "loading",
                "Looking for your face",
                "Position your face inside the frame.",
                "fa-solid fa-user"
            );


            startScanning();

        } catch (error) {

            console.error(
                "Camera error:",
                error
            );

            setCameraStatus(
                "Camera unavailable"
            );

            setStatus(
                "error",
                "Camera access required",
                "Please allow camera permission and try again.",
                "fa-solid fa-video-slash"
            );
        }
    }


    // ========================================================
    // STOP CAMERA
    // ========================================================

    function stopCamera() {

        if (scanTimer) {

            clearInterval(
                scanTimer
            );

            scanTimer = null;
        }


        if (cameraStream) {

            cameraStream
                .getTracks()
                .forEach(
                    track => track.stop()
                );

            cameraStream = null;
        }


        if (video) {
            video.srcObject = null;
        }

        setCameraStatus(
            "Camera stopped"
        );
    }


    // ========================================================
    // CAPTURE IMAGE
    // ========================================================

    function captureImage() {

        if (!video.videoWidth) {
            return null;
        }


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
            0.85
        );
    }


    // ========================================================
    // START SCANNING
    // ========================================================

    function startScanning() {

        if (scanTimer) {

            clearInterval(
                scanTimer
            );
        }


        scanTimer =
            setInterval(
                scanFace,
                1200
            );


        // Scan immediately
        scanFace();
    }


    // ========================================================
    // FACE DETECTION
    // ========================================================

    async function scanFace() {

        if (
            isProcessing ||
            faceRegistered ||
            !cameraStream
        ) {
            return;
        }


        const image =
            captureImage();


        if (!image) {
            return;
        }


        isProcessing = true;


        try {

            const formData =
                new FormData();

            formData.append(
                "image",
                image
            );


            const response =
                await fetch(
                    detectUrl,
                    {
                        method: "POST",
                        headers: {
                            "X-CSRFToken":
                                getCookie(
                                    "csrftoken"
                                )
                        },
                        body: formData
                    }
                );


            const data =
                await response.json();


            // ------------------------------------------------
            // NO FACE
            // ------------------------------------------------

            if (
                data.face_count === 0
            ) {

                setStatus(
                    "loading",
                    "No face detected",
                    "Please move your face inside the frame.",
                    "fa-solid fa-user-slash"
                );

                return;
            }


            // ------------------------------------------------
            // MULTIPLE FACES
            // ------------------------------------------------

            if (
                data.face_count > 1
            ) {

                setStatus(
                    "error",
                    "Multiple faces detected",
                    "Only one person is allowed. Please make sure nobody else is visible.",
                    "fa-solid fa-users"
                );

                return;
            }


            // ------------------------------------------------
            // ONE FACE
            // ------------------------------------------------

            if (
                data.face_count === 1
            ) {

                setStatus(
                    "loading",
                    "Face detected",
                    "Generating your secure Face ID...",
                    "fa-solid fa-fingerprint"
                );


                faceRegistered = true;


                if (scanTimer) {

                    clearInterval(
                        scanTimer
                    );

                    scanTimer = null;
                }


                await saveFace(
                    image
                );
            }

        } catch (error) {

            console.error(
                "Face detection error:",
                error
            );

            setStatus(
                "error",
                "Connection error",
                "Unable to communicate with the Face ID service.",
                "fa-solid fa-triangle-exclamation"
            );

            faceRegistered = false;

        } finally {

            isProcessing = false;
        }
    }


    // ========================================================
    // SAVE FACE ID
    // ========================================================

    async function saveFace(image) {

        try {

            const formData =
                new FormData();

            formData.append(
                "image",
                image
            );


            const response =
                await fetch(
                    saveUrl,
                    {
                        method: "POST",
                        headers: {
                            "X-CSRFToken":
                                getCookie(
                                    "csrftoken"
                                )
                        },
                        body: formData
                    }
                );


            const data =
                await response.json();


            if (
                data.success
            ) {

                setStatus(
                    "success",
                    "Face ID registration successful!",
                    "Your account is ready. Redirecting to login...",
                    "fa-solid fa-circle-check"
                );


                stopCamera();


                // Wait so user can see
                // successful registration
                setTimeout(
                    function () {

                        window.location.href =
                            "/login/";

                    },
                    2000
                );


            } else {

                faceRegistered = false;

                setStatus(
                    "error",
                    "Face ID registration failed",
                    data.message ||
                        "Unable to save your Face ID.",
                    "fa-solid fa-circle-xmark"
                );

                startScanning();
            }

        } catch (error) {

            console.error(
                "Face save error:",
                error
            );

            faceRegistered = false;

            setStatus(
                "error",
                "Unable to save Face ID",
                "Please try again.",
                "fa-solid fa-triangle-exclamation"
            );

            startScanning();
        }
    }


    // ========================================================
    // STOP BUTTON
    // ========================================================

    if (stopCameraBtn) {

        stopCameraBtn.addEventListener(
            "click",
            function () {

                stopCamera();

                setStatus(
                    "loading",
                    "Camera stopped",
                    "Click Retry Camera to continue Face ID registration.",
                    "fa-solid fa-video-slash"
                );
            }
        );
    }


    // ========================================================
    // RETRY BUTTON
    // ========================================================

    if (retryCameraBtn) {

        retryCameraBtn.addEventListener(
            "click",
            function () {

                startCamera();
            }
        );
    }


    // ========================================================
    // CLEANUP
    // ========================================================

    window.addEventListener(
        "beforeunload",
        function () {

            stopCamera();
        }
    );


    // ========================================================
    // START AUTOMATICALLY
    // ========================================================

    startCamera();

});