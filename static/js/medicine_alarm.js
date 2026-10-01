(function () {

    let triggeredMedicines = {};


    async function checkMedicineAlarm() {

        try {

            const response = await fetch(
                "/medicine/alarm-check/"
            );

            if (!response.ok) {
                return;
            }

            const data = await response.json();

            if (!data.success) {
                return;
            }

            data.medicines.forEach(function (medicine) {

                const key =
                    medicine.id + "_" + medicine.time;

                if (triggeredMedicines[key]) {
                    return;
                }

                triggeredMedicines[key] = true;

                showMedicineAlarm(medicine);

            });

        } catch (error) {

            console.log(
                "Medicine alarm check failed:",
                error
            );

        }

    }


    function showMedicineAlarm(medicine) {

        // Browser notification
        if (
            "Notification" in window &&
            Notification.permission === "granted"
        ) {

            new Notification(
                "Medicine Reminder",
                {
                    body:
                        medicine.medicine_name +
                        "\nDosage: " +
                        medicine.dosage +
                        "\nTime: " +
                        medicine.time,

                    icon: "/static/images/ai.png"
                }
            );

        }


        // Alarm sound
        playAlarmSound();


        // Screen alarm
        const alarm =
            document.createElement("div");

        alarm.className =
            "medicine-alarm-popup";


        alarm.innerHTML = `
            <div class="medicine-alarm-icon">
                <i class="fa-solid fa-pills"></i>
            </div>

            <div class="medicine-alarm-content">

                <h3>Medicine Reminder</h3>

                <p>
                    <strong>
                        ${medicine.medicine_name}
                    </strong>
                </p>

                <span>
                    Dosage: ${medicine.dosage}
                </span>

                <span>
                    Scheduled: ${medicine.time}
                </span>

            </div>

            <button
                type="button"
                class="medicine-alarm-close"
                aria-label="Dismiss alarm"
            >
                <i class="fa-solid fa-xmark"></i>
            </button>
        `;


        document.body.appendChild(alarm);


        alarm.querySelector(
            ".medicine-alarm-close"
        ).addEventListener(
            "click",
            function () {

                alarm.remove();

            }
        );


        setTimeout(
            function () {

                if (alarm.parentNode) {
                    alarm.remove();
                }

            },
            30000
        );

    }


    // ==========================================
    // MEDICINE ALARM SOUND
    // ==========================================

    function playAlarmSound() {

        try {

            const AudioContext =
                window.AudioContext ||
                window.webkitAudioContext;


            if (!AudioContext) {
                return;
            }


            const audioContext =
                new AudioContext();


            // Make sure audio context is running
            if (
                audioContext.state === "suspended"
            ) {

                audioContext.resume();

            }


            const startTime =
                audioContext.currentTime;


            /*
             * Medical alarm pattern:
             *
             * BEEP
             * BEEP
             * HIGH BEEP
             *
             * pause
             *
             * BEEP
             * BEEP
             * HIGH BEEP
             */


            function createBeep(
                start,
                frequency,
                duration
            ) {

                const oscillator =
                    audioContext.createOscillator();

                const gainNode =
                    audioContext.createGain();


                oscillator.type = "sine";


                oscillator.frequency.setValueAtTime(
                    frequency,
                    start
                );


                // Start quietly
                gainNode.gain.setValueAtTime(
                    0.001,
                    start
                );


                // Quick volume increase
                gainNode.gain.exponentialRampToValueAtTime(
                    0.30,
                    start + 0.03
                );


                // Smooth volume decrease
                gainNode.gain.exponentialRampToValueAtTime(
                    0.001,
                    start + duration
                );


                oscillator.connect(
                    gainNode
                );

                gainNode.connect(
                    audioContext.destination
                );


                oscillator.start(start);

                oscillator.stop(
                    start + duration
                );

            }


            // First alarm sequence

            createBeep(
                startTime,
                880,
                0.25
            );


            createBeep(
                startTime + 0.35,
                880,
                0.25
            );


            createBeep(
                startTime + 0.70,
                1047,
                0.40
            );


            // Second alarm sequence

            createBeep(
                startTime + 1.45,
                880,
                0.25
            );


            createBeep(
                startTime + 1.80,
                880,
                0.25
            );


            createBeep(
                startTime + 2.15,
                1047,
                0.40
            );


            // Close audio context
            setTimeout(
                function () {

                    audioContext.close();

                },
                3000
            );


        } catch (error) {

            console.log(
                "Alarm sound could not play:",
                error
            );

        }

    }


    // ==========================================
    // NOTIFICATION PERMISSION
    // ==========================================

    function requestNotificationPermission() {

        if (
            "Notification" in window &&
            Notification.permission === "default"
        ) {

            Notification.requestPermission();

        }

    }


    // ==========================================
    // START MEDICINE ALARM SYSTEM
    // ==========================================

    window.addEventListener(
        "load",
        function () {

            requestNotificationPermission();


            // Check immediately
            checkMedicineAlarm();


            // Check every 10 seconds
            setInterval(
                checkMedicineAlarm,
                10000
            );

        }
    );

})();