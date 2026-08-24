/* ============================================================
   OCRFlow - Document OCR Frontend
============================================================ */


/* ============================================================
   DOM ELEMENTS
============================================================ */

const dropZone =
    document.getElementById("dropZone");

const fileInput =
    document.getElementById("fileInput");

const browseButton =
    document.getElementById("browseButton");

const fileInfo =
    document.getElementById("fileInfo");

const fileName =
    document.getElementById("fileName");

const fileSize =
    document.getElementById("fileSize");

const removeFileButton =
    document.getElementById("removeFile");

const extractButton =
    document.getElementById("extractButton");

const statusBox =
    document.getElementById("status");

const statusTitle =
    document.getElementById("statusTitle");

const statusMessage =
    document.getElementById("statusMessage");

const resultsBox =
    document.getElementById("results");


/* ============================================================
   STATE
============================================================ */

let selectedFile = null;


/* ============================================================
   CONFIGURATION
============================================================ */

const MAX_FILE_SIZE =
    50 * 1024 * 1024;

const ALLOWED_EXTENSIONS = [
    "jpg",
    "jpeg",
    "png",
    "bmp",
    "webp",
    "tif",
    "tiff",
    "pdf"
];


/* ============================================================
   INITIALIZATION
============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        initializeFormatCards();

    }
);


/* ============================================================
   BROWSE FILES
============================================================ */

if (browseButton) {

    browseButton.addEventListener(
        "click",
        (event) => {

            event.stopPropagation();

            fileInput.click();

        }
    );

}


/* ============================================================
   DROP ZONE CLICK
============================================================ */

dropZone.addEventListener(
    "click",
    (event) => {

        /*
         * Don't trigger file picker if the user
         * clicked the browse button.
         */

        if (
            event.target.closest(
                "#browseButton"
            )
        ) {
            return;
        }

        fileInput.click();

    }
);


/* ============================================================
   FILE INPUT
============================================================ */

fileInput.addEventListener(
    "change",
    () => {

        if (
            fileInput.files &&
            fileInput.files.length > 0
        ) {

            setFile(
                fileInput.files[0]
            );

        }

    }
);


/* ============================================================
   DRAG OVER
============================================================ */

dropZone.addEventListener(
    "dragover",
    (event) => {

        event.preventDefault();

        dropZone.classList.add(
            "dragover"
        );

    }
);


/* ============================================================
   DRAG LEAVE
============================================================ */

dropZone.addEventListener(
    "dragleave",
    (event) => {

        /*
         * Only remove the state when the pointer
         * actually leaves the drop zone.
         */

        if (
            !dropZone.contains(
                event.relatedTarget
            )
        ) {

            dropZone.classList.remove(
                "dragover"
            );

        }

    }
);


/* ============================================================
   DROP
============================================================ */

dropZone.addEventListener(
    "drop",
    (event) => {

        event.preventDefault();

        dropZone.classList.remove(
            "dragover"
        );

        const files =
            event.dataTransfer.files;

        if (
            files &&
            files.length > 0
        ) {

            setFile(
                files[0]
            );

        }

    }
);


/* ============================================================
   SET FILE
============================================================ */

function setFile(file) {

    /*
     * Validate extension
     */

    const extension =
        getFileExtension(
            file.name
        );


    if (
        !ALLOWED_EXTENSIONS.includes(
            extension
        )
    ) {

        showStatus(
            "Invalid file",
            `Supported formats: JPG, PNG, WEBP, TIFF and PDF.`,
            "error"
        );

        return;

    }


    /*
     * Validate file size
     */

    if (
        file.size > MAX_FILE_SIZE
    ) {

        showStatus(
            "File too large",
            "Maximum allowed file size is 50 MB.",
            "error"
        );

        return;

    }


    /*
     * Save selected file
     */

    selectedFile = file;


    /*
     * Update file name
     */

    if (fileName) {

        fileName.textContent =
            file.name;

    }


    /*
     * Update file size
     */

    if (fileSize) {

        fileSize.textContent =
            formatFileSize(
                file.size
            );

    }


    /*
     * Show file information
     */

    fileInfo.classList.remove(
        "hidden"
    );


    /*
     * Enable extraction
     */

    extractButton.disabled = false;


    /*
     * Clear previous results
     */

    resultsBox.classList.add(
        "hidden"
    );

    resultsBox.innerHTML = "";


    /*
     * Clear status
     */

    statusBox.classList.add(
        "hidden"
    );

}


/* ============================================================
   REMOVE FILE
============================================================ */

if (removeFileButton) {

    removeFileButton.addEventListener(
        "click",
        (event) => {

            event.stopPropagation();

            clearFile();

        }
    );

}


function clearFile() {

    selectedFile = null;

    fileInput.value = "";

    fileInfo.classList.add(
        "hidden"
    );

    extractButton.disabled = true;

    resultsBox.classList.add(
        "hidden"
    );

    resultsBox.innerHTML = "";

    statusBox.classList.add(
        "hidden"
    );

}


/* ============================================================
   FORMAT CARDS
============================================================ */

function initializeFormatCards() {

    const formatCards =
        document.querySelectorAll(
            ".format-card"
        );


    formatCards.forEach(
        (card) => {

            const radio =
                card.querySelector(
                    'input[type="radio"]'
                );


            card.addEventListener(
                "click",
                () => {

                    /*
                     * Remove selected state
                     * from all cards.
                     */

                    formatCards.forEach(
                        (item) => {

                            item.classList.remove(
                                "selected"
                            );

                        }
                    );


                    /*
                     * Select current card.
                     */

                    card.classList.add(
                        "selected"
                    );


                    /*
                     * Check radio.
                     */

                    if (radio) {

                        radio.checked = true;

                    }

                }
            );


            /*
             * Support keyboard/radio interaction.
             */

            if (radio) {

                radio.addEventListener(
                    "change",
                    () => {

                        formatCards.forEach(
                            (item) => {

                                item.classList.remove(
                                    "selected"
                                );

                            }
                        );


                        card.classList.add(
                            "selected"
                        );

                    }
                );

            }

        }
    );

}


/* ============================================================
   GET OUTPUT FORMAT
============================================================ */

function getOutputFormat() {

    const selected =
        document.querySelector(
            'input[name="outputFormat"]:checked'
        );


    if (!selected) {

        return "both";

    }


    return selected.value;

}


/* ============================================================
   EXTRACT DOCUMENT
============================================================ */

extractButton.addEventListener(
    "click",
    async () => {

        if (!selectedFile) {

            showStatus(
                "No document selected",
                "Please upload an image or PDF first.",
                "error"
            );

            return;

        }


        /*
         * Create FormData
         */

        const formData =
            new FormData();


        formData.append(
            "file",
            selectedFile
        );


        formData.append(
            "output_format",
            getOutputFormat()
        );


        /*
         * Disable button
         */

        setProcessingState(
            true
        );


        /*
         * Show processing status
         */

        showStatus(
            "Processing document",
            "PaddleOCR is extracting text and tables...",
            "loading"
        );


        try {

            const startTime =
                performance.now();


            const response =
                await fetch(
                    "/api/extract",
                    {
                        method: "POST",
                        body: formData
                    }
                );


            /*
             * Try to parse JSON
             */

            let data;

            try {

                data =
                    await response.json();

            } catch {

                throw new Error(
                    "Server returned an invalid response."
                );

            }


            /*
             * Handle API errors
             */

            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    data.message ||
                    "OCR processing failed."
                );

            }


            /*
             * Calculate frontend time
             */

            const endTime =
                performance.now();

            const frontendTime =
                (
                    (endTime - startTime)
                    / 1000
                ).toFixed(2);


            /*
             * Processing time from backend
             */

            const backendTime =
                data.processing_time_seconds ??
                frontendTime;


            /*
             * Success
             */

            showStatus(
                "Extraction completed",
                `Document processed successfully in ${backendTime}s.`,
                "success"
            );


            /*
             * Render download results
             */

            renderResults(
                data
            );


        } catch (error) {

            console.error(
                "OCR Error:",
                error
            );


            showStatus(
                "Extraction failed",
                error.message ||
                "Something went wrong while processing the document.",
                "error"
            );


        } finally {

            setProcessingState(
                false
            );

        }

    }
);


/* ============================================================
   PROCESSING STATE
============================================================ */

function setProcessingState(
    processing
) {

    if (processing) {

        extractButton.disabled = true;

        extractButton.classList.add(
            "loading"
        );

    } else {

        extractButton.disabled =
            !selectedFile;

        extractButton.classList.remove(
            "loading"
        );

    }

}


/* ============================================================
   STATUS
============================================================ */

function showStatus(
    title,
    message,
    type = "loading"
) {

    statusBox.classList.remove(
        "hidden"
    );


    /*
     * Reset classes.
     */

    statusBox.className =
        `status ${type}`;


    /*
     * Update title.
     */

    if (statusTitle) {

        statusTitle.textContent =
            title;

    }


    /*
     * Update message.
     */

    if (statusMessage) {

        statusMessage.textContent =
            message;

    }


    /*
     * Update status indicator.
     */

    const statusIcon =
        statusBox.querySelector(
            ".status-icon"
        );


    if (statusIcon) {

        statusIcon.style.background =
            getStatusColor(type);

        statusIcon.style.boxShadow =
            `0 0 12px ${getStatusColor(type)}`;

    }

}


/* ============================================================
   STATUS COLORS
============================================================ */

function getStatusColor(
    type
) {

    if (type === "success") {

        return "#22c55e";

    }


    if (type === "error") {

        return "#ef4444";

    }


    return "#6366f1";

}


/* ============================================================
   RESULTS
============================================================ */

function renderResults(data) {

    resultsBox.classList.remove(
        "hidden"
    );


    /*
     * Safely get values.
     */

    const pageCount =
        Number(
            data.page_count || 0
        );


    const files =
        Array.isArray(
            data.files
        )
            ? data.files
            : [];


    /*
     * Build result header.
     */

    let html = `

        <div class="results-header">

            <div>

                <span class="results-success">
                    ✓ Extraction complete
                </span>

                <h3>
                    Your files are ready
                </h3>

                <p>
                    ${pageCount}
                    ${pageCount === 1 ? "page" : "pages"}
                    processed successfully.
                </p>

            </div>

        </div>

        <div class="download-list">

    `;


    /*
     * No files returned.
     */

    if (files.length === 0) {

        html += `

            <div class="no-results">

                No downloadable files were
                returned by the server.

            </div>

        `;

    }


    /*
     * Download buttons.
     */

    for (
        const file of files
    ) {

        const format =
            String(
                file.format || ""
            ).toLowerCase();


        const label =
            getFormatLabel(
                format
            );


        const icon =
            getFormatIcon(
                format
            );


        html += `

            <a
                class="download-button"
                href="${escapeAttribute(
                    file.download_url
                )}"
                download
            >

                <span class="download-icon">
                    ${icon}
                </span>

                <span class="download-content">

                    <strong>
                        Download ${label}
                    </strong>

                    <small>
                        ${getFormatDescription(format)}
                    </small>

                </span>

                <span class="download-arrow">
                    ↓
                </span>

            </a>

        `;

    }


    html += `

        </div>

    `;


    resultsBox.innerHTML =
        html;

}


/* ============================================================
   FORMAT HELPERS
============================================================ */

function getFormatLabel(
    format
) {

    if (format === "docx") {

        return "Word";

    }


    if (format === "xlsx") {

        return "Excel";

    }


    return format.toUpperCase();

}


function getFormatIcon(
    format
) {

    if (format === "docx") {

        return "W";

    }


    if (format === "xlsx") {

        return "X";

    }


    return "↓";

}


function getFormatDescription(
    format
) {

    if (format === "docx") {

        return "Microsoft Word document";

    }


    if (format === "xlsx") {

        return "Microsoft Excel spreadsheet";

    }


    return "Generated document";

}


/* ============================================================
   FILE EXTENSION
============================================================ */

function getFileExtension(
    filename
) {

    const parts =
        filename.split(".");


    if (parts.length < 2) {

        return "";

    }


    return parts
        .pop()
        .toLowerCase();

}


/* ============================================================
   FILE SIZE
============================================================ */

function formatFileSize(
    bytes
) {

    if (bytes === 0) {

        return "0 Bytes";

    }


    const units = [
        "Bytes",
        "KB",
        "MB",
        "GB"
    ];


    const index =
        Math.floor(
            Math.log(bytes)
            / Math.log(1024)
        );


    return (
        bytes /
        Math.pow(
            1024,
            index
        )
    ).toFixed(
        index === 0 ? 0 : 2
    )
    + " "
    + units[index];

}


/* ============================================================
   HTML ESCAPING
============================================================ */

function escapeHtml(
    value
) {

    return String(value)
        .replaceAll(
            "&",
            "&amp;"
        )
        .replaceAll(
            "<",
            "&lt;"
        )
        .replaceAll(
            ">",
            "&gt;"
        )
        .replaceAll(
            '"',
            "&quot;"
        )
        .replaceAll(
            "'",
            "&#039;"
        );

}


function escapeAttribute(
    value
) {

    return escapeHtml(
        value
    );

}