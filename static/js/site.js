document.addEventListener("DOMContentLoaded", () => {
    const phoneInputs = Array.from(document.querySelectorAll("[data-phone-input='true']"));

    const getPhoneDigits = (value, maxDigits) => {
        let digits = String(value || "").replace(/\D/g, "");
        if (digits.length >= maxDigits + 1 && /^[78]/.test(digits)) {
            digits = digits.slice(1);
        }
        return digits.slice(0, maxDigits);
    };

    const formatPhoneValue = (digits) => {
        if (!digits.length) {
            return "";
        }

        let formattedValue = "+7";

        if (digits.length > 0) {
            formattedValue += ` (${digits.slice(0, 3)}`;
        }

        if (digits.length >= 3) {
            formattedValue += ")";
        }

        if (digits.length > 3) {
            formattedValue += ` ${digits.slice(3, 6)}`;
        }

        if (digits.length > 6) {
            formattedValue += `-${digits.slice(6, 8)}`;
        }

        if (digits.length > 8) {
            formattedValue += `-${digits.slice(8, 10)}`;
        }

        return formattedValue;
    };

    const countDigitsBeforeCaret = (value, caretPosition) => {
        const digits = String(value || "")
            .slice(0, caretPosition)
            .replace(/\D/g, "");
        if (digits.startsWith("7")) {
            return Math.max(0, digits.length - 1);
        }
        return digits.length;
    };

    const getCaretPositionForDigitIndex = (value, digitIndex) => {
        if (digitIndex <= 0) {
            return value.startsWith("+7") ? Math.min(value.length, 4) : 0;
        }

        let seenDigits = 0;
        for (let index = 0; index < value.length; index += 1) {
            if (/\d/.test(value[index])) {
                if (value.startsWith("+7") && index === 1) {
                    continue;
                }
                seenDigits += 1;
            }

            if (seenDigits >= digitIndex) {
                return index + 1;
            }
        }

        return value.length;
    };

    const setMaskedValue = (input, digits, digitIndex) => {
        const formattedValue = formatPhoneValue(digits);
        input.value = formattedValue;

        if (typeof digitIndex !== "number") {
            return;
        }

        const caretPosition = getCaretPositionForDigitIndex(formattedValue, digitIndex);
        input.setSelectionRange(caretPosition, caretPosition);
    };

    const applyPhoneFormatting = (input, digitIndex) => {
        const maxDigits = Number(input.dataset.phoneDigits || 10);
        const digits = getPhoneDigits(input.value, maxDigits);
        setMaskedValue(input, digits, digitIndex);

        if (digits.length && digits.length < maxDigits) {
            input.setCustomValidity(`Введите ${maxDigits} цифр номера телефона.`);
        } else {
            input.setCustomValidity("");
        }

        if (digits.length && digits.length < maxDigits) {
            input.setCustomValidity(`Введите ${maxDigits} цифр номера телефона.`);
        }
    };

    const removeDigitNearCaret = (input, direction) => {
        const selectionStart = input.selectionStart || 0;
        const maxDigits = Number(input.dataset.phoneDigits || 10);
        const digits = getPhoneDigits(input.value, maxDigits);

        if (!digits.length) {
            return false;
        }

        const digitIndex = direction === "backward"
            ? countDigitsBeforeCaret(input.value, selectionStart) - 1
            : countDigitsBeforeCaret(input.value, selectionStart);

        if (digitIndex < 0 || digitIndex >= digits.length) {
            return false;
        }

        const nextDigits = digits.slice(0, digitIndex) + digits.slice(digitIndex + 1);
        setMaskedValue(input, nextDigits, digitIndex);
        input.setCustomValidity(
            nextDigits.length && nextDigits.length < maxDigits
                ? `Введите ${maxDigits} цифр номера телефона.`
                : ""
        );
        return true;
    };

    phoneInputs.forEach((input) => {
        input.addEventListener("blur", () => {
            applyPhoneFormatting(input);
        });

        input.addEventListener("input", () => {
            const digitIndex = countDigitsBeforeCaret(input.value, input.selectionStart || 0);
            applyPhoneFormatting(input, digitIndex);
        });

        input.addEventListener("paste", (event) => {
            event.preventDefault();
            const pastedText = (event.clipboardData || window.clipboardData).getData("text");
            const maxDigits = Number(input.dataset.phoneDigits || 10);
            input.value = pastedText;
            applyPhoneFormatting(input, getPhoneDigits(pastedText, maxDigits).length);
        });

        input.addEventListener("keydown", (event) => {
            const hasSelection = input.selectionStart !== input.selectionEnd;
            const isModifierKey = event.ctrlKey || event.metaKey;

            if (event.key === "Backspace" && !hasSelection) {
                const charBeforeCaret = input.value[(input.selectionStart || 0) - 1];

                if (charBeforeCaret && !/\d/.test(charBeforeCaret)) {
                    event.preventDefault();
                    removeDigitNearCaret(input, "backward");
                }
                return;
            }

            if (event.key === "Delete" && !hasSelection) {
                const charAfterCaret = input.value[input.selectionStart || 0];

                if (charAfterCaret && !/\d/.test(charAfterCaret)) {
                    event.preventDefault();
                    removeDigitNearCaret(input, "forward");
                }
                return;
            }

            if ([46, 8, 9, 27, 13].includes(event.keyCode) ||
                isModifierKey ||
                (event.keyCode >= 35 && event.keyCode <= 39)) {
                return;
            }

            if ((event.keyCode < 48 || event.keyCode > 57) && (event.keyCode < 96 || event.keyCode > 105)) {
                event.preventDefault();
            }
        });

        if (input.value.trim()) {
            applyPhoneFormatting(input);
        }
    });

    const body = document.body;
    const header = document.getElementById("site-header");
    const navCollapse = document.getElementById("mainNav");
    const lightbox = document.getElementById("lightbox");
    const lightboxImage = document.getElementById("lightbox-image");
    const lightboxTitle = document.getElementById("lightbox-title");
    const lightboxText = document.getElementById("lightbox-text");

    window.requestAnimationFrame(() => {
        body.classList.add("loaded");
    });

    const syncHeaderState = () => {
        if (!header) {
            return;
        }
        header.classList.toggle("is-scrolled", window.scrollY > 16);
    };

    syncHeaderState();
    window.addEventListener("scroll", syncHeaderState, { passive: true });

    const revealElements = document.querySelectorAll(".reveal");
    if ("IntersectionObserver" in window) {
        const revealObserver = new IntersectionObserver(
            (entries, observer) => {
                entries.forEach((entry) => {
                    if (!entry.isIntersecting) {
                        return;
                    }
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                });
            },
            {
                threshold: 0.08,
                rootMargin: "0px 0px 4% 0px",
            }
        );

        revealElements.forEach((item) => revealObserver.observe(item));
    } else {
        revealElements.forEach((item) => item.classList.add("is-visible"));
    }

    document.querySelectorAll("a[href*='#']").forEach((anchor) => {
        anchor.addEventListener("click", (event) => {
            const href = anchor.getAttribute("href");
            if (!href || href === "#") {
                return;
            }

            let targetUrl;
            try {
                targetUrl = new URL(href, window.location.href);
            } catch {
                return;
            }

            if (!targetUrl.hash) {
                return;
            }
            if (targetUrl.origin !== window.location.origin || targetUrl.pathname !== window.location.pathname) {
                return;
            }

            const target = document.querySelector(targetUrl.hash);
            if (!target) {
                return;
            }

            event.preventDefault();
            const offset = header ? header.offsetHeight + 18 : 96;
            const top = target.getBoundingClientRect().top + window.pageYOffset - offset;

            window.scrollTo({
                top,
                behavior: "smooth",
            });

            if (navCollapse && navCollapse.classList.contains("show") && window.bootstrap) {
                const collapseInstance = bootstrap.Collapse.getInstance(navCollapse);
                collapseInstance?.hide();
            }
        });
    });

    let lastLightboxTrigger = null;

    const openLightbox = (trigger) => {
        if (!lightbox || !lightboxImage || !lightboxTitle || !lightboxText) {
            return;
        }

        lastLightboxTrigger = trigger;
        lightboxImage.src = trigger.dataset.lightboxImage || "";
        lightboxImage.alt = trigger.querySelector("img")?.alt || trigger.dataset.lightboxTitle || "";
        lightboxTitle.textContent = trigger.dataset.lightboxTitle || "";
        lightboxText.textContent = trigger.dataset.lightboxText || "";
        lightbox.hidden = false;

        window.requestAnimationFrame(() => {
            lightbox.classList.add("is-open");
            body.classList.add("lightbox-open");
        });
    };

    const closeLightbox = () => {
        if (!lightbox || lightbox.hidden) {
            return;
        }

        lightbox.classList.remove("is-open");
        body.classList.remove("lightbox-open");

        window.setTimeout(() => {
            lightbox.hidden = true;
            lightboxImage.src = "";
            if (lastLightboxTrigger) {
                lastLightboxTrigger.focus();
            }
        }, 220);
    };

    document.querySelectorAll("[data-lightbox-image]").forEach((trigger) => {
        trigger.addEventListener("click", () => openLightbox(trigger));
    });

    lightbox?.querySelectorAll("[data-lightbox-close]").forEach((closer) => {
        closer.addEventListener("click", closeLightbox);
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeLightbox();
        }
    });

    const repeatableFileFields = document.querySelectorAll("[data-repeatable-file-field]");
    repeatableFileFields.forEach((field) => {
        const fieldName = field.dataset.fieldName || "";
        const isRequired = field.dataset.required === "true";
        const pickerInput = field.querySelector("[data-file-picker]");
        const hiddenInputsContainer = field.querySelector("[data-hidden-inputs]");
        const fileList = field.querySelector("[data-file-list]");
        const emptyState = field.querySelector("[data-file-empty]");
        const countBadge = field.querySelector("[data-file-count]");
        const addButton = field.querySelector("[data-file-picker-trigger]");
        const errorBlock = field.querySelector("[data-file-error]");

        if (!fieldName || !pickerInput || !hiddenInputsContainer || !fileList || !countBadge) {
            return;
        }

        let storedFiles = [];

        const buildHiddenInput = (fileItem) => {
            const hiddenInput = document.createElement("input");
            hiddenInput.type = "file";
            hiddenInput.name = fieldName;
            hiddenInput.tabIndex = -1;
            hiddenInput.setAttribute("aria-hidden", "true");

            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(fileItem.file);
            hiddenInput.files = dataTransfer.files;
            hiddenInput.dataset.fileId = fileItem.id;
            hiddenInput.className = "d-none";
            return hiddenInput;
        };

        const hideError = () => {
            pickerInput.setCustomValidity("");
            errorBlock?.classList.add("d-none");
            field.classList.remove("is-invalid");
        };

        const showError = () => {
            pickerInput.setCustomValidity("Добавьте хотя бы один файл.");
            errorBlock?.classList.remove("d-none");
            field.classList.add("is-invalid");
        };

        const renderFiles = () => {
            hiddenInputsContainer.innerHTML = "";
            const renderedItems = fileList.querySelectorAll("[data-file-item]");
            renderedItems.forEach((item) => item.remove());

            storedFiles.forEach((fileItem) => {
                hiddenInputsContainer.appendChild(buildHiddenInput(fileItem));

                const item = document.createElement("div");
                item.className = "multi-file-item d-flex justify-content-between align-items-center gap-3";
                item.dataset.fileItem = fileItem.id;
                item.innerHTML = `
                    <div class="d-flex align-items-center gap-2 min-w-0">
                        <span class="badge text-bg-light border">new</span>
                        <span class="multi-file-name" title="${fileItem.file.name}">${fileItem.file.name}</span>
                    </div>
                    <button type="button" class="btn btn-sm btn-outline-danger flex-shrink-0" data-remove-file="${fileItem.id}">
                        Убрать
                    </button>
                `;
                fileList.appendChild(item);
            });

            countBadge.textContent = String(storedFiles.length);
            if (emptyState) {
                emptyState.classList.toggle("d-none", storedFiles.length > 0);
            }

            if (!isRequired || storedFiles.length > 0) {
                hideError();
            }
        };

        addButton?.addEventListener("click", () => {
            pickerInput.click();
        });

        pickerInput.addEventListener("change", () => {
            const freshFiles = Array.from(pickerInput.files || []);
            freshFiles.forEach((fileItem) => {
                storedFiles.push({
                    id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
                    file: fileItem,
                });
            });
            pickerInput.value = "";
            renderFiles();
        });

        fileList.addEventListener("click", (event) => {
            const removeButton = event.target.closest("[data-remove-file]");
            if (!removeButton) {
                return;
            }

            const fileId = removeButton.dataset.removeFile;
            storedFiles = storedFiles.filter((fileItem) => fileItem.id !== fileId);
            renderFiles();
        });

        field.addEventListener("validate-repeatable-files", () => {
            if (isRequired && storedFiles.length === 0) {
                showError();
            } else {
                hideError();
            }
        });

        renderFiles();
    });

    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    [...popoverTriggerList].forEach(
        (element) =>
            new bootstrap.Popover(element, {
                container: "body",
            })
    );

    const siteHeaderPanel = document.getElementById("siteHeaderPanel");
    if (siteHeaderPanel) {
        const siteHeaderCollapse = bootstrap.Collapse.getOrCreateInstance(siteHeaderPanel, { toggle: false });
        siteHeaderPanel.querySelectorAll("a").forEach((link) => {
            link.addEventListener("click", () => {
                if (window.innerWidth < 992) {
                    siteHeaderCollapse.hide();
                }
            });
        });
    }

    const colorModeInput = document.getElementById("id_color_mode");
    const colorTemplateNameInput = document.getElementById("id_color_template_name");
    const hiddenColorInputPrimary = document.getElementById("id_color_preference");
    const hiddenColorInputAccent = document.getElementById("id_color_accent");
    const hiddenColorInputBackground = document.getElementById("id_color_background");
    const hiddenColorInputExtra = document.getElementById("id_color_extra");
    const customColorInputPrimary = document.querySelector("[data-custom-color-input='primary']");
    const customColorInputAccent = document.querySelector("[data-custom-color-input='accent']");
    const customColorInputBackground = document.querySelector("[data-custom-color-input='background']");
    const customColorInputExtra = document.querySelector("[data-custom-color-input='extra']");
    const customColorValuePrimary = document.querySelector("[data-custom-color-value='primary']");
    const customColorValueAccent = document.querySelector("[data-custom-color-value='accent']");
    const customColorValueBackground = document.querySelector("[data-custom-color-value='background']");
    const customColorValueExtra = document.querySelector("[data-custom-color-value='extra']");
    const customColorPreviewPrimary = document.querySelector("[data-custom-color-preview='primary']");
    const customColorPreviewAccent = document.querySelector("[data-custom-color-preview='accent']");
    const customColorPreviewBackground = document.querySelector("[data-custom-color-preview='background']");
    const customColorPreviewExtra = document.querySelector("[data-custom-color-preview='extra']");
    const colorPreviewPrimary = document.querySelectorAll("[data-color-preview-primary]");
    const colorPreviewAccent = document.querySelectorAll("[data-color-preview-accent]");
    const colorPreviewBackground = document.querySelectorAll("[data-color-preview-background]");
    const colorPreviewExtra = document.querySelectorAll("[data-color-preview-extra]");
    const colorSourceLabels = document.querySelectorAll("[data-color-source]");
    const inlineColorSummaries = document.querySelectorAll("[data-color-inline-summary]");
    const templateProjectCards = document.querySelectorAll(".template-project-card");
    const templateProjectButtons = document.querySelectorAll("[data-template-select]");
    const templateProjectMedia = document.querySelectorAll(".project-sample-card__media");
    const projectsTabButton = document.getElementById("brief-colors-projects-tab");
    const customTabButton = document.getElementById("brief-colors-custom-tab");
    const projectsTabPane = document.getElementById("brief-colors-projects");
    const customTabPane = document.getElementById("brief-colors-custom");
    const normalizeHex = (value) => String(value || "").trim().toLowerCase();
    const defaultPalette = ["#14344c", "#c96f3b", "#f4f1ea", "#2b506b"];

    const normalizePalette = (colors) => {
        const safeColors = [...colors];
        while (safeColors.length < 4) {
            safeColors.push(defaultPalette[safeColors.length]);
        }
        return safeColors.slice(0, 4).map((color, index) => {
            const normalized = normalizeHex(color);
            return /^#[0-9a-f]{6}$/.test(normalized) ? normalized : defaultPalette[index];
        });
    };

    const hiddenPaletteInputs = [
        hiddenColorInputPrimary,
        hiddenColorInputAccent,
        hiddenColorInputBackground,
        hiddenColorInputExtra,
    ];

    const customPaletteInputs = [
        customColorInputPrimary,
        customColorInputAccent,
        customColorInputBackground,
        customColorInputExtra,
    ];

    const customPaletteValueLabels = [
        customColorValuePrimary,
        customColorValueAccent,
        customColorValueBackground,
        customColorValueExtra,
    ];

    const customPalettePreviewChips = [
        customColorPreviewPrimary,
        customColorPreviewAccent,
        customColorPreviewBackground,
        customColorPreviewExtra,
    ];

    let lastSelectedTemplateName = colorTemplateNameInput?.value || "";
    let lastSelectedTemplateColors = null;
    let customPaletteDirty = colorModeInput?.value === "custom";

    const readPaletteFromInputs = (inputs) => normalizePalette(
        inputs.map((input, index) => input?.value || defaultPalette[index])
    );

    const writePaletteToInputs = (inputs, colors) => {
        const safeColors = normalizePalette(colors);
        inputs.forEach((input, index) => {
            if (!input) {
                return;
            }
            const value = safeColors[index];
            input.setAttribute("value", value);
            input.defaultValue = value;
            input.value = "#000000";
            input.value = value;
        });
        return safeColors;
    };

    const updateCustomPaletteValueLabels = (colors = getCustomColors()) => {
        const safeColors = normalizePalette(colors);
        customPaletteValueLabels.forEach((label, index) => {
            if (!label) {
                return;
            }
            label.textContent = safeColors[index];
        });
        customPalettePreviewChips.forEach((chip, index) => {
            if (!chip) {
                return;
            }
            chip.style.backgroundColor = safeColors[index];
        });
        return safeColors;
    };

    const refreshCustomPaletteVisualState = (colors, source = "custom-visual-refresh") => {
        const safeColors = normalizePalette(colors);
        writePaletteToCustomInputs(safeColors);
        updateCustomPaletteValueLabels(safeColors);
        return safeColors;
    };

    const scheduleCustomPaletteVisualRefresh = (colors, source = "custom-visual-refresh") => {
        const safeColors = normalizePalette(colors);
        refreshCustomPaletteVisualState(safeColors, `${source}:immediate`);
        window.requestAnimationFrame(() => {
            refreshCustomPaletteVisualState(safeColors, `${source}:raf`);
        });
        window.setTimeout(() => {
            refreshCustomPaletteVisualState(safeColors, `${source}:timeout`);
        }, 0);
        return safeColors;
    };

    const getStoredColors = () => readPaletteFromInputs(hiddenPaletteInputs);
    const getCustomColors = () => readPaletteFromInputs(customPaletteInputs);
    const writePaletteToHiddenInputs = (colors) => writePaletteToInputs(hiddenPaletteInputs, colors);
    const writePaletteToCustomInputs = (colors) => writePaletteToInputs(customPaletteInputs, colors);

    const getPaletteFromCard = (card) => normalizePalette([
        card?.dataset.colorPrimary || card?.getAttribute("data-color-primary"),
        card?.dataset.colorAccent || card?.getAttribute("data-color-accent"),
        card?.dataset.colorBackground || card?.getAttribute("data-color-background"),
        card?.dataset.colorExtra || card?.getAttribute("data-color-extra"),
    ]);

    const findTemplateCardByName = (name) => [...templateProjectCards].find(
        (card) => card.dataset.templateName === name
    );

    const rememberTemplatePalette = (name, colors, source) => {
        lastSelectedTemplateName = name || "";
        lastSelectedTemplateColors = normalizePalette(colors);
        customPaletteDirty = false;
        return lastSelectedTemplateColors;
    };

    const updateColorPreview = (colors = getStoredColors()) => {
        const [primary, accent, background, extra] = normalizePalette(colors);
        colorPreviewPrimary.forEach((element) => {
            element.style.backgroundColor = primary;
        });
        colorPreviewAccent.forEach((element) => {
            element.style.backgroundColor = accent;
        });
        colorPreviewBackground.forEach((element) => {
            element.style.backgroundColor = background;
        });
        colorPreviewExtra.forEach((element) => {
            element.style.backgroundColor = extra;
        });
    };

    const updateInlineColorSummaryVisibility = () => {
        if (!inlineColorSummaries.length) {
            return;
        }
        const showInlineSummary = colorModeInput?.value === "custom";
        inlineColorSummaries.forEach((element) => {
            element.classList.toggle("d-none", !showInlineSummary);
        });
    };

    const updateTemplateSelection = (selectedName) => {
        templateProjectCards.forEach((card) => {
            card.classList.toggle("is-selected", Boolean(selectedName) && card.dataset.templateName === selectedName);
        });
    };

    const setColorTabState = (mode) => {
        const isCustom = mode === "custom";

        if (projectsTabButton) {
            projectsTabButton.classList.toggle("active", !isCustom);
            projectsTabButton.setAttribute("aria-selected", String(!isCustom));
        }
        if (customTabButton) {
            customTabButton.classList.toggle("active", isCustom);
            customTabButton.setAttribute("aria-selected", String(isCustom));
        }
        if (projectsTabPane) {
            projectsTabPane.classList.toggle("show", !isCustom);
            projectsTabPane.classList.toggle("active", !isCustom);
        }
        if (customTabPane) {
            customTabPane.classList.toggle("show", isCustom);
            customTabPane.classList.toggle("active", isCustom);
        }

    };

    const updateColorModeLabel = () => {
        if (!colorSourceLabels.length || !colorModeInput) {
            return;
        }
        let label = "По шаблону";
        if (colorModeInput.value === "custom") {
            label = "Кастомная палитра";
        } else if (colorTemplateNameInput?.value) {
            label = `Шаблон: ${colorTemplateNameInput.value}`;
        }
        colorSourceLabels.forEach((element) => {
            element.textContent = label;
        });
    };

    const syncColorSummaryState = (colors = getStoredColors(), source = "summary-sync") => {
        const safeColors = normalizePalette(colors);
        updateColorPreview(safeColors);
        updateCustomPaletteValueLabels(safeColors);
        updateColorModeLabel();
        updateInlineColorSummaryVisibility();
        return safeColors;
    };

    const selectTemplatePalette = (card, source = "template-select") => {
        if (!card || !colorModeInput) {
            return;
        }
        const templateName = card.dataset.templateName || "";
        const rememberedColors = rememberTemplatePalette(templateName, getPaletteFromCard(card), source);
        const syncedColors = writePaletteToHiddenInputs(rememberedColors);
        scheduleCustomPaletteVisualRefresh(syncedColors, `${source}:template-sync`);
        colorModeInput.value = "template";
        setColorTabState("template");
        if (colorTemplateNameInput) {
            colorTemplateNameInput.value = templateName;
        }
        updateTemplateSelection(templateName);
        syncColorSummaryState(syncedColors, source);
    };

    const getColorsForCustomMode = () => {
        if (lastSelectedTemplateColors && !customPaletteDirty) {
            return normalizePalette(lastSelectedTemplateColors);
        }
        if (customPaletteInputs.some(Boolean)) {
            return getCustomColors();
        }
        return getStoredColors();
    };

    const activateCustomPalette = (source = "custom-activate") => {
        const sourceColors = getColorsForCustomMode();
        setColorTabState("custom");
        const syncedCustomColors = scheduleCustomPaletteVisualRefresh(sourceColors, source);
        const syncedHiddenColors = writePaletteToHiddenInputs(syncedCustomColors);
        if (colorModeInput) {
            colorModeInput.value = "custom";
        }
        if (colorTemplateNameInput) {
            colorTemplateNameInput.value = "";
        }
        updateTemplateSelection("");
        syncColorSummaryState(syncedHiddenColors, source);
        return syncedHiddenColors;
    };

    templateProjectButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const card = button.closest(".template-project-card");
            if (!card) {
                return;
            }
            selectTemplatePalette(card, "template-button-click");
        });
    });

    templateProjectCards.forEach((card) => {
        card.addEventListener("click", (event) => {
            if (event.target.closest("a") || event.target.closest("[data-template-select]")) {
                return;
            }
            selectTemplatePalette(card, "template-card-click");
        });
    });

    templateProjectMedia.forEach((media) => {
        const resetZoomOrigin = () => {
            media.style.setProperty("--zoom-origin-x", "50%");
            media.style.setProperty("--zoom-origin-y", "50%");
        };

        const updateZoomOrigin = (event) => {
            if (event.pointerType === "touch") {
                return;
            }
            const rect = media.getBoundingClientRect();
            if (!rect.width || !rect.height) {
                return;
            }

            const relativeX = ((event.clientX - rect.left) / rect.width) * 100;
            const relativeY = ((event.clientY - rect.top) / rect.height) * 100;
            const clampPercent = (value) => Math.min(100, Math.max(0, value));

            media.style.setProperty("--zoom-origin-x", `${clampPercent(relativeX).toFixed(2)}%`);
            media.style.setProperty("--zoom-origin-y", `${clampPercent(relativeY).toFixed(2)}%`);
        };

        resetZoomOrigin();
        media.addEventListener("pointerenter", updateZoomOrigin);
        media.addEventListener("pointermove", updateZoomOrigin);
        media.addEventListener("pointerleave", resetZoomOrigin);
    });

    const projectSliders = document.querySelectorAll("[data-project-slider]");
    projectSliders.forEach((slider) => {
        const track = slider.querySelector("[data-slider-track]");
        const slides = slider.querySelectorAll("[data-slider-slide]");
        const prevButton = slider.querySelector("[data-slider-prev]");
        const nextButton = slider.querySelector("[data-slider-next]");
        const currentLabel = slider.querySelector("[data-slider-current]");
        const totalLabel = slider.querySelector("[data-slider-total]");
        const projectLink = slider.dataset.projectLink;
        const projectLinkExternal = slider.dataset.projectLinkExternal === "true";

        if (!track || !slides.length) {
            return;
        }

        const slideCount = slides.length;
        let activeIndex = 0;

        const syncSlider = () => {
            track.style.transform = `translateX(-${activeIndex * 100}%)`;
            slider.dataset.sliderStatic = String(slideCount <= 1);
            if (currentLabel) {
                currentLabel.textContent = String(activeIndex + 1);
            }
            if (totalLabel) {
                totalLabel.textContent = String(slideCount);
            }
        };

        const stepSlider = (step) => {
            if (slideCount <= 1) {
                return;
            }
            activeIndex = (activeIndex + step + slideCount) % slideCount;
            syncSlider();
        };

        prevButton?.addEventListener("click", () => stepSlider(-1));
        nextButton?.addEventListener("click", () => stepSlider(1));
        const openProjectLink = () => {
            if (!projectLink) {
                return;
            }

            if (projectLinkExternal) {
                window.open(projectLink, "_blank", "noopener");
                return;
            }

            window.location.href = projectLink;
        };

        slider.addEventListener("click", (event) => {
            if (event.target.closest("[data-slider-prev], [data-slider-next]")) {
                return;
            }
            openProjectLink();
        });
        slider.addEventListener("keydown", (event) => {
            if (event.key === "Enter") {
                event.preventDefault();
                openProjectLink();
            }
            if (event.key === "ArrowLeft") {
                event.preventDefault();
                stepSlider(-1);
            }
            if (event.key === "ArrowRight") {
                event.preventDefault();
                stepSlider(1);
            }
        });

        syncSlider();
    });

    const customColorInputs = customPaletteInputs.filter(Boolean);
    customColorInputs.forEach((input) => {
        input.addEventListener("input", () => {
            const syncedColors = scheduleCustomPaletteVisualRefresh(getCustomColors(), `custom-input:${input.dataset.customColorInput || "unknown"}`);
            writePaletteToHiddenInputs(syncedColors);
            customPaletteDirty = true;
            if (colorModeInput) {
                colorModeInput.value = "custom";
            }
            setColorTabState("custom");
            if (colorTemplateNameInput) {
                colorTemplateNameInput.value = "";
            }
            updateTemplateSelection("");
            syncColorSummaryState(syncedColors, `custom-input:${input.dataset.customColorInput || "unknown"}`);
        });
    });

    const activateProjectsPalette = (source = "projects-tab-click") => {
        const selectedCard = findTemplateCardByName(colorTemplateNameInput?.value || "")
            || findTemplateCardByName(lastSelectedTemplateName)
            || templateProjectCards[0];
        if (selectedCard) {
            selectTemplatePalette(selectedCard, source);
        } else {
            if (colorModeInput) {
                colorModeInput.value = "template";
            }
            setColorTabState("template");
            syncColorSummaryState(getStoredColors(), `${source}:no-template`);
        }
    };

    projectsTabButton?.addEventListener("click", () => {
        activateProjectsPalette("projects-tab-click");
    });

    customTabButton?.addEventListener("click", () => {
        activateCustomPalette("custom-tab-click");
    });

    if (colorModeInput?.value === "template" && templateProjectCards.length) {
        const selectedCard = findTemplateCardByName(colorTemplateNameInput?.value || "") || templateProjectCards[0];
        selectTemplatePalette(selectedCard, "initial-template-state");
    } else {
        setColorTabState("custom");
        const initialColors = scheduleCustomPaletteVisualRefresh(getStoredColors(), "initial-custom-state");
        writePaletteToHiddenInputs(initialColors);
        syncColorSummaryState(initialColors, "initial-custom-state");
    }

    const forms = document.querySelectorAll(".needs-validation");
    [...forms].forEach((form) => {
        form.addEventListener("submit", (event) => {
            form.querySelectorAll("[data-repeatable-file-field]").forEach((field) => {
                field.dispatchEvent(new CustomEvent("validate-repeatable-files"));
            });
            const invalidField = [...form.elements].find((field) => {
                if (!field || typeof field.checkValidity !== "function") {
                    return false;
                }
                if (field.disabled || field.type === "hidden") {
                    return false;
                }
                return !field.checkValidity();
            });
            if (invalidField) {
                event.preventDefault();
                event.stopPropagation();
                invalidField.focus();
            }
            form.classList.add("was-validated");
        });
    });

    const pricingConfigElement = document.getElementById("brief-pricing-config");
    const briefForm = document.querySelector("[data-brief-pricing]");
    if (pricingConfigElement && briefForm) {
        const pricingConfig = JSON.parse(pricingConfigElement.textContent);
        const shouldResetServiceDefaults = briefForm.dataset.resetServiceDefaults === "true";
        const clientTypeField = document.getElementById("id_client_type");
        const businessNameLabel = document.getElementById("business-name-label");
        const businessNameInput = document.getElementById("id_business_name");
        const siteTypeField = document.getElementById("id_site_type");
        const extraPagesField = document.getElementById("id_extra_pages");
        const hostingField = document.getElementById("id_need_hosting");
        const hostingPlanField = document.getElementById("id_hosting_plan");
        const hostingPlanWrapper = document.querySelector("[data-hosting-plan-wrapper]");
        const domainField = document.getElementById("id_need_domain");
        const logoDesignField = document.getElementById("id_need_logo_design");
        const basicSeoField = document.getElementById("id_need_basic_seo");
        const photoSelectionField = document.getElementById("id_need_photo_selection");
        const emailFormField = document.getElementById("id_need_email_form");
        const reviewsSectionField = document.getElementById("id_need_reviews_section");
        const estimatedPriceField = document.getElementById("id_estimated_price");
        const summaryService = document.querySelector("[data-summary-service]");
        const summaryBase = document.querySelector("[data-summary-base]");
        const summaryTotal = document.querySelector("[data-summary-total]");
        const summaryBreakdown = document.querySelector("[data-summary-breakdown]");
        const summaryBreakdownEmpty = document.querySelector("[data-summary-breakdown-empty]");

        const addonFields = [
            { element: domainField, key: "need_domain" },
            { element: logoDesignField, key: "need_logo_design" },
            { element: basicSeoField, key: "need_basic_seo" },
            { element: photoSelectionField, key: "need_photo_selection" },
            { element: emailFormField, key: "need_email_form" },
            { element: reviewsSectionField, key: "need_reviews_section" },
        ];
        const summaryToggleMap = new Map(
            [
                ["need_hosting", hostingField],
                ...addonFields.map(({ element, key }) => [key, element]),
            ].filter(([, element]) => element)
        );

        const formatRub = (value) => {
            const amount = Number(value || 0);
            const hasFraction = Math.abs(amount - Math.round(amount)) > 0.001;
            return `${amount.toLocaleString("ru-RU", {
                minimumFractionDigits: hasFraction ? 2 : 0,
                maximumFractionDigits: 2,
            })} ₽`;
        };

        const getPositiveInteger = (value) => {
            const number = Number.parseInt(String(value || "0"), 10);
            if (Number.isNaN(number) || number < 0) {
                return 0;
            }
            return number;
        };

        const updateBusinessNameLabel = () => {
            if (!clientTypeField || !businessNameLabel || !businessNameInput) {
                return;
            }
            const isLegalEntity = clientTypeField.value === "legal_entity";
            businessNameLabel.textContent = isLegalEntity ? "Наименование компании" : "Имя";
            businessNameInput.placeholder = isLegalEntity ? "ООО Ромашка" : "Иван Иванов";
        };

        const updateHostingPlanVisibility = () => {
            const isEnabled = Boolean(hostingField?.checked);
            if (hostingPlanWrapper) {
                hostingPlanWrapper.classList.toggle("d-none", !isEnabled);
            }
            if (hostingPlanField) {
                hostingPlanField.disabled = !isEnabled;
                if (!isEnabled) {
                    hostingPlanField.value = "monthly";
                }
            }
        };

        const toggleSummaryOption = (key, isChecked) => {
            const targetField = summaryToggleMap.get(key);
            if (!targetField) {
                return;
            }
            targetField.checked = isChecked;
            if (key === "need_hosting") {
                updateHostingPlanVisibility();
            }
            updatePricing();
        };

        const renderBreakdown = (rows) => {
            if (!summaryBreakdown) {
                return;
            }

            summaryBreakdown.querySelectorAll("[data-summary-row]").forEach((row) => row.remove());
            if (summaryBreakdownEmpty) {
                summaryBreakdownEmpty.classList.toggle("d-none", rows.length > 0);
            }

            rows.forEach((row) => {
                if (row.kind === "detail") {
                    const rowElement = document.createElement("div");
                    const labelElement = document.createElement("span");
                    const valueElement = document.createElement("strong");

                    rowElement.className = "brief-price-breakdown__row brief-price-breakdown__row--detail";
                    rowElement.dataset.summaryRow = "true";
                    labelElement.textContent = row.label;
                    valueElement.textContent = formatRub(row.value);

                    rowElement.appendChild(labelElement);
                    rowElement.appendChild(valueElement);
                    summaryBreakdown.appendChild(rowElement);
                    return;
                }

                const rowElement = document.createElement("div");
                const checkboxElement = document.createElement("input");
                const copyElement = document.createElement("span");
                const labelElement = document.createElement("label");
                const metaElement = document.createElement("span");
                const valueElement = document.createElement("strong");
                const checkboxId = `brief-summary-${row.key}`;

                rowElement.className = "home-summary-option brief-summary-option";
                rowElement.dataset.summaryRow = "true";
                checkboxElement.type = "checkbox";
                checkboxElement.className = "form-check-input home-summary-option__check";
                checkboxElement.id = checkboxId;
                checkboxElement.checked = Boolean(row.checked);
                checkboxElement.setAttribute("aria-label", row.label);
                checkboxElement.addEventListener("change", () => {
                    toggleSummaryOption(row.key, checkboxElement.checked);
                });
                copyElement.className = "home-summary-option__copy";
                labelElement.className = "home-summary-option__label";
                labelElement.setAttribute("for", checkboxId);
                labelElement.textContent = row.label;
                metaElement.className = "home-summary-option__meta";
                metaElement.textContent = row.meta || "";
                metaElement.classList.toggle("d-none", !row.meta);
                valueElement.className = "home-summary-option__value";
                valueElement.textContent = formatRub(row.value);

                copyElement.appendChild(labelElement);
                if (row.meta) {
                    copyElement.appendChild(metaElement);
                }
                rowElement.appendChild(checkboxElement);
                rowElement.appendChild(copyElement);
                rowElement.appendChild(valueElement);
                summaryBreakdown.appendChild(rowElement);
            });
        };

        const updatePricing = () => {
            if (!siteTypeField || !summaryService || !summaryBase || !summaryTotal) {
                return;
            }

            const basePrice = Number(pricingConfig.site_type_prices[siteTypeField.value] || 0);
            const extraPages = getPositiveInteger(extraPagesField?.value);
            const extraPagesPrice = extraPages * Number(pricingConfig.extra_page_price || 0);
            const hostingPlanValue = hostingPlanField?.value || "monthly";
            const hostingPrice = hostingField && hostingField.checked
                ? Number(pricingConfig.hosting_plan_prices?.[hostingPlanValue] || 0)
                : 0;

            let total = basePrice + extraPagesPrice + hostingPrice;
            const breakdownRows = [];

            if (extraPages > 0) {
                breakdownRows.push({
                    kind: "detail",
                    label: `${pricingConfig.addon_summary_labels?.extra_pages || "Доп. страницы"} x${extraPages}`,
                    value: extraPagesPrice,
                });
            }

            if (hostingPrice > 0) {
                breakdownRows.push({
                    kind: "toggle",
                    key: "need_hosting",
                    label: pricingConfig.hosting_summary_labels?.[hostingPlanValue] || "Хостинг сайта",
                    value: hostingPrice,
                    checked: true,
                });
            }

            addonFields.forEach(({ element, key }) => {
                if (!element?.checked) {
                    return;
                }
                const addonPrice = Number(pricingConfig.addon_prices?.[key] || 0);
                total += addonPrice;
                breakdownRows.push({
                    kind: "toggle",
                    key,
                    label: pricingConfig.addon_summary_labels?.[key] || key,
                    value: addonPrice,
                    checked: true,
                });
            });

            summaryService.textContent = siteTypeField.options[siteTypeField.selectedIndex]?.text || "";
            summaryBase.textContent = formatRub(basePrice);
            summaryTotal.textContent = formatRub(total);
            renderBreakdown(breakdownRows);
            if (estimatedPriceField) {
                estimatedPriceField.value = total.toFixed(2);
            }
        };

        if (shouldResetServiceDefaults) {
            if (siteTypeField) {
                siteTypeField.value = "single_page";
            }
            if (extraPagesField) {
                extraPagesField.value = "0";
            }
            if (hostingField) {
                hostingField.checked = false;
            }
            if (hostingPlanField) {
                hostingPlanField.value = "monthly";
            }
            addonFields.forEach(({ element }) => {
                if (element) {
                    element.checked = false;
                }
            });
        }

        updateBusinessNameLabel();
        updateHostingPlanVisibility();
        updatePricing();

        clientTypeField?.addEventListener("change", updateBusinessNameLabel);
        siteTypeField?.addEventListener("change", updatePricing);
        extraPagesField?.addEventListener("input", updatePricing);
        extraPagesField?.addEventListener("change", updatePricing);
        hostingField?.addEventListener("change", () => {
            updateHostingPlanVisibility();
            updatePricing();
        });
        hostingPlanField?.addEventListener("change", updatePricing);
        addonFields.forEach(({ element }) => {
            element?.addEventListener("change", updatePricing);
        });
    }

    const contactShell = document.querySelector("[data-contact-email]");
    const contactEmail = contactShell?.dataset.contactEmail?.trim();
    const contactPhoneHref = contactShell?.dataset.contactPhoneHref?.trim();
    const contactPhoneText = contactShell?.dataset.contactPhoneText?.trim();

    if (contactEmail) {
        document.querySelectorAll("[data-contact-email-link]").forEach((link) => {
            link.setAttribute("href", `mailto:${contactEmail}`);
        });

        document.querySelectorAll("[data-contact-email-text]").forEach((node) => {
            node.textContent = contactEmail;
        });
    }

    if (contactPhoneHref) {
        document.querySelectorAll("[data-contact-phone-link]").forEach((link) => {
            link.setAttribute("href", `tel:${contactPhoneHref}`);
        });
    }

    if (contactPhoneText) {
        document.querySelectorAll("[data-contact-phone-text]").forEach((node) => {
            node.textContent = contactPhoneText;
        });
    }

    const homeServiceConfigElement = document.getElementById("home-service-config");
    const homeServicePicker = document.querySelector("[data-home-service-picker]");
    if (homeServiceConfigElement && homeServicePicker) {
        const homeServiceConfig = JSON.parse(homeServiceConfigElement.textContent);
        const briefUrl = homeServicePicker.dataset.briefUrl || "";
        const siteDevelopmentField = homeServicePicker.querySelector("[data-home-select='site_development']");
        const siteOptions = homeServicePicker.querySelector("[data-home-site-options]");
        const siteTypeFields = [...homeServicePicker.querySelectorAll("[data-home-site-type]")];
        const extraPagesField = homeServicePicker.querySelector("[data-home-extra-pages]");
        const hostingField = homeServicePicker.querySelector("[data-home-select='hosting']");
        const hostingOptions = homeServicePicker.querySelector("[data-home-hosting-options]");
        const hostingPlanFields = [...homeServicePicker.querySelectorAll("[data-home-hosting-plan]")];
        const addonFields = [...homeServicePicker.querySelectorAll("[data-home-select]")].filter(
            (field) => !["site_development", "hosting"].includes(field.dataset.homeSelect || "")
        );
        const summaryWidget = homeServicePicker.querySelector("[data-home-summary-widget]");
        const summaryList = homeServicePicker.querySelector("[data-home-summary-list]");
        const summaryEmpty = homeServicePicker.querySelector("[data-home-summary-empty]");
        const summaryTotal = homeServicePicker.querySelector("[data-home-summary-total]");
        const summaryLink = homeServicePicker.querySelector("[data-home-summary-link]");
        const summaryTotalBlock = summaryTotal?.closest(".brief-price-total");
        const summaryAction = summaryLink;
        const serviceFieldByKey = new Map(
            [
                ["site_development", siteDevelopmentField],
                ["hosting", hostingField],
                ...addonFields.map((field) => [field.dataset.homeSelect || "", field]),
            ].filter(([key, field]) => key && field)
        );
        let summaryEmptyDismissed = false;

        const summaryEmptyClose = summaryWidget?.querySelector("[data-home-summary-empty-close]");
        summaryTotalBlock?.classList.add("d-none");
        summaryAction?.classList.add("d-none");

        const formatRub = (value) => {
            const amount = Number(value || 0);
            const hasFraction = Math.abs(amount - Math.round(amount)) > 0.001;
            return `${amount.toLocaleString("ru-RU", {
                minimumFractionDigits: hasFraction ? 2 : 0,
                maximumFractionDigits: 2,
            })} ₽`;
        };

        const getPositiveInteger = (value) => {
            const number = Number.parseInt(String(value || "0"), 10);
            if (Number.isNaN(number) || number < 0) {
                return 0;
            }
            return number;
        };

        const getCheckedValue = (fields, fallback) =>
            fields.find((field) => field.checked)?.value || fallback;

        const setRowSelected = (key, isSelected) => {
            const row = homeServicePicker.querySelector(`[data-home-service='${key}']`);
            if (!row) {
                return;
            }
            if (isSelected) {
                row.setAttribute("data-selected", "true");
            } else {
                row.removeAttribute("data-selected");
            }
        };

        const toggleOptionsBlock = (element, isVisible) => {
            element?.classList.toggle("d-none", !isVisible);
        };

        const toggleServiceFromSummary = (key, isChecked) => {
            const field = serviceFieldByKey.get(key);
            if (!field) {
                return;
            }
            field.checked = isChecked;
            updateHomeServiceSummary();
        };

        const renderSummaryRows = (rows) => {
            if (!summaryList) {
                return;
            }

            summaryList.querySelectorAll("[data-home-summary-row]").forEach((row) => row.remove());
            const normalizedRows = [];

            if (siteDevelopmentField?.checked) {
                const siteType = getCheckedValue(siteTypeFields, "single_page");
                normalizedRows.push({
                    kind: "service",
                    key: "site_development",
                    label: "Написание сайта",
                    meta: siteType === "catalog" ? "Сайт-каталог" : "Одностраничник",
                    value: Number(homeServiceConfig.site_type_prices?.[siteType] || 0),
                    checked: true,
                });

                const extraPages = getPositiveInteger(extraPagesField?.value);
                if (extraPages > 0) {
                    normalizedRows.push({
                        kind: "detail",
                        label: `Доп. страницы x${extraPages}`,
                        value: extraPages * Number(homeServiceConfig.extra_page_price || 0),
                    });
                }
            }

            if (hostingField?.checked) {
                const hostingPlan = getCheckedValue(hostingPlanFields, "monthly");
                normalizedRows.push({
                    kind: "service",
                    key: "hosting",
                    label: "Хостинг сайта",
                    meta: hostingPlan === "quarterly" ? "550 ₽ при оплате 3 месяцев" : "750 ₽/мес",
                    value: Number(homeServiceConfig.hosting_plan_prices?.[hostingPlan] || 0),
                    checked: true,
                });
            }

            addonFields.forEach((field) => {
                if (!field.checked) {
                    return;
                }

                const rowKey = field.dataset.homeSelect || "";
                const fieldName = field.dataset.homeField || "";
                if (!rowKey || !fieldName) {
                    return;
                }

                normalizedRows.push({
                    kind: "service",
                    key: rowKey,
                    label: field.closest("[data-home-service]")?.querySelector(".terra-service-row__title")?.textContent?.trim() || fieldName,
                    value: Number(homeServiceConfig.addon_prices?.[fieldName] || 0),
                    checked: true,
                });
            });

            if (summaryEmpty) {
                summaryEmpty.classList.toggle("d-none", normalizedRows.length > 0);
            }

            normalizedRows.forEach((row) => {
                if (row.kind === "detail") {
                    const rowElement = document.createElement("div");
                    const labelElement = document.createElement("span");
                    const valueElement = document.createElement("strong");

                    rowElement.className = "brief-price-breakdown__row brief-price-breakdown__row--detail";
                    rowElement.dataset.homeSummaryRow = "true";
                    labelElement.textContent = row.label;
                    valueElement.textContent = formatRub(row.value);

                    rowElement.appendChild(labelElement);
                    rowElement.appendChild(valueElement);
                    summaryList.appendChild(rowElement);
                    return;
                }

                const rowElement = document.createElement("div");
                const checkboxElement = document.createElement("input");
                const copyElement = document.createElement("span");
                const labelElement = document.createElement("span");
                const metaElement = document.createElement("span");
                const valueElement = document.createElement("strong");

                rowElement.className = "home-summary-option";
                rowElement.dataset.homeSummaryRow = "true";
                checkboxElement.type = "checkbox";
                checkboxElement.className = "form-check-input home-summary-option__check";
                checkboxElement.checked = Boolean(row.checked);
                checkboxElement.addEventListener("change", () => {
                    toggleServiceFromSummary(row.key, checkboxElement.checked);
                });
                copyElement.className = "home-summary-option__copy";
                labelElement.className = "home-summary-option__label";
                labelElement.textContent = row.label;
                metaElement.className = "home-summary-option__meta";
                metaElement.textContent = row.meta || "";
                metaElement.classList.toggle("d-none", !row.meta);
                valueElement.className = "home-summary-option__value";
                valueElement.textContent = formatRub(row.value);

                copyElement.appendChild(labelElement);
                copyElement.appendChild(metaElement);
                rowElement.appendChild(checkboxElement);
                rowElement.appendChild(copyElement);
                rowElement.appendChild(valueElement);
                summaryList.appendChild(rowElement);
            });
        };

        if (extraPagesField) {
            extraPagesField.value = "0";
        }
        siteTypeFields.forEach((field) => {
            field.checked = field.value === "single_page";
        });
        if (hostingField) {
            hostingField.checked = false;
        }
        hostingPlanFields.forEach((field) => {
            field.checked = field.value === "monthly";
        });
        addonFields.forEach((field) => {
            field.checked = false;
        });

        const updateHomeServiceSummary = () => {
            const rows = [];
            const params = new URLSearchParams();
            let total = 0;

            const siteSelected = Boolean(siteDevelopmentField?.checked);
            setRowSelected("site_development", siteSelected);
            toggleOptionsBlock(siteOptions, siteSelected);

            if (siteSelected) {
                const siteType = getCheckedValue(siteTypeFields, "single_page");
                const sitePrice = Number(homeServiceConfig.site_type_prices?.[siteType] || 0);
                const siteLabel = siteType === "catalog"
                    ? "Написание сайта: сайт-каталог"
                    : "Написание сайта: одностраничник";
                rows.push({ label: siteLabel, value: sitePrice });
                total += sitePrice;
                params.set("site_type", siteType);

                const extraPages = getPositiveInteger(extraPagesField?.value);
                if (extraPages > 0) {
                    const extraPagesPrice = extraPages * Number(homeServiceConfig.extra_page_price || 0);
                    rows.push({ label: `Доп. страницы x${extraPages}`, value: extraPagesPrice });
                    total += extraPagesPrice;
                    params.set("extra_pages", String(extraPages));
                }
            }

            const hostingSelected = Boolean(hostingField?.checked);
            setRowSelected("hosting", hostingSelected);
            toggleOptionsBlock(hostingOptions, hostingSelected);

            if (hostingSelected) {
                const hostingPlan = getCheckedValue(hostingPlanFields, "monthly");
                const hostingPrice = Number(homeServiceConfig.hosting_plan_prices?.[hostingPlan] || 0);
                const hostingLabel = hostingPlan === "quarterly"
                    ? "Хостинг сайта: 3 месяца"
                    : "Хостинг сайта: 1 месяц";

                rows.push({ label: hostingLabel, value: hostingPrice });
                total += hostingPrice;
                params.set("need_hosting", "1");
                params.set("hosting_plan", hostingPlan);
            }

            addonFields.forEach((field) => {
                const rowKey = field.dataset.homeSelect || "";
                const fieldName = field.dataset.homeField || "";
                const isSelected = field.checked;

                setRowSelected(rowKey, isSelected);
                if (!isSelected || !fieldName) {
                    return;
                }

                const addonPrice = Number(homeServiceConfig.addon_prices?.[fieldName] || 0);
                const label = field.closest("[data-home-service]")?.querySelector(".terra-service-row__title")?.textContent?.trim() || fieldName;

                rows.push({ label, value: addonPrice });
                total += addonPrice;
                params.set(fieldName, "1");
            });

            renderSummaryRows(rows);
            const hasRows = rows.length > 0;
            const showEmptyPrompt = !hasRows && !summaryEmptyDismissed;

            summaryWidget?.classList.toggle("d-none", !hasRows && !showEmptyPrompt);
            summaryWidget?.classList.toggle("brief-price-widget--idle", showEmptyPrompt);
            summaryEmpty?.classList.toggle("d-none", !showEmptyPrompt);
            summaryTotalBlock?.classList.toggle("d-none", !hasRows);
            summaryAction?.classList.toggle("d-none", !hasRows);
            if (summaryTotal) {
                summaryTotal.textContent = formatRub(total);
            }
            if (summaryLink) {
                summaryLink.href = hasRows && briefUrl ? `${briefUrl}?${params.toString()}` : briefUrl;
            }
        };

        summaryEmptyClose?.addEventListener("click", () => {
            summaryEmptyDismissed = true;
            updateHomeServiceSummary();
        });

        siteDevelopmentField?.addEventListener("change", updateHomeServiceSummary);
        siteTypeFields.forEach((field) => {
            field.addEventListener("change", updateHomeServiceSummary);
        });
        extraPagesField?.addEventListener("input", updateHomeServiceSummary);
        extraPagesField?.addEventListener("change", updateHomeServiceSummary);
        hostingField?.addEventListener("change", updateHomeServiceSummary);
        hostingPlanFields.forEach((field) => {
            field.addEventListener("change", updateHomeServiceSummary);
        });
        addonFields.forEach((field) => {
            field.addEventListener("change", updateHomeServiceSummary);
        });

        updateHomeServiceSummary();
    }

    const guideAnchors = [...document.querySelectorAll("[data-guide-step]")]
        .map((element) => ({
            element,
            step: Number.parseInt(element.dataset.guideStep || "0", 10),
            title: element.dataset.guideTitle || "",
            text: element.dataset.guideCopy || "",
            emoji: element.dataset.guideEmoji || "✨",
            placement: element.dataset.guidePlacement || "bottom",
            passive: element.dataset.guidePassive === "true",
        }))
        .filter((item) => item.step > 0)
        .sort((left, right) => left.step - right.step);

    if (guideAnchors.length) {
        const safeStorage = {
            get(key) {
                try {
                    return window.sessionStorage.getItem(key);
                } catch {
                    return null;
                }
            },
            set(key, value) {
                try {
                    window.sessionStorage.setItem(key, value);
                } catch {
                    // Ignore storage failures in private mode or strict browser settings.
                }
            },
        };
        const guideScope = body.classList.contains("terra-home-page")
            ? "home"
            : body.classList.contains("brief-form-page")
                ? "brief-form"
                : window.location.pathname;
        const storageKey = `nova-guide-dismissed:${guideScope}`;
        const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
        const launcher = document.createElement("button");
        launcher.type = "button";
        launcher.className = "nova-guide-launcher";
        launcher.setAttribute("aria-label", "Открыть подсказки по странице");
        launcher.innerHTML = `
            <span class="nova-guide-launcher__emoji" aria-hidden="true">✨</span>
            <span class="nova-guide-launcher__label">Подсказки</span>
        `;

        const guide = document.createElement("aside");
        guide.className = "nova-guide";
        guide.setAttribute("aria-live", "polite");
        guide.setAttribute("aria-hidden", "true");
        guide.innerHTML = `
            <div class="nova-guide__bubble">
                <button type="button" class="nova-guide__close" aria-label="Скрыть подсказку">×</button>
                <div class="nova-guide__top">
                    <div class="nova-guide__avatar" aria-hidden="true">✨</div>
                    <div class="nova-guide__copy">
                        <span class="nova-guide__eyebrow">Навигатор</span>
                        <h3 class="nova-guide__title"></h3>
                        <p class="nova-guide__text"></p>
                    </div>
                </div>
                <div class="nova-guide__footer">
                    <span class="nova-guide__progress"></span>
                    <div class="nova-guide__actions">
                        <button type="button" class="nova-guide__button" data-guide-dismiss>Скрыть</button>
                        <button type="button" class="nova-guide__button nova-guide__button--primary" data-guide-next>Дальше</button>
                    </div>
                </div>
            </div>
        `;

        body.appendChild(launcher);
        body.appendChild(guide);

        const guideAvatar = guide.querySelector(".nova-guide__avatar");
        const guideTitle = guide.querySelector(".nova-guide__title");
        const guideText = guide.querySelector(".nova-guide__text");
        const guideProgress = guide.querySelector(".nova-guide__progress");
        const guideNext = guide.querySelector("[data-guide-next]");
        const guideDismiss = guide.querySelector("[data-guide-dismiss]");
        const guideClose = guide.querySelector(".nova-guide__close");

        let activeGuideIndex = 0;
        let activeGuideTarget = null;
        let guideOpen = false;
        let positionFrame = 0;

        const clamp = (value, min, max) => Math.min(Math.max(value, min), max);
        const isMobileGuide = () => window.innerWidth < 768;

        const clearGuideTarget = () => {
            activeGuideTarget?.classList.remove("guide-focus-target");
            activeGuideTarget = null;
            body.classList.remove("guide-hero-intro-active");
            body.classList.remove("guide-overlay-active");
        };

        const queueGuidePosition = () => {
            if (!guideOpen) {
                return;
            }
            if (positionFrame) {
                window.cancelAnimationFrame(positionFrame);
            }
            positionFrame = window.requestAnimationFrame(() => {
                positionFrame = 0;
                positionGuide();
            });
        };

        const pickPlacement = (preferred, rect, width, height) => {
            const padding = 20;
            const available = {
                top: rect.top - padding,
                bottom: window.innerHeight - rect.bottom - padding,
                left: rect.left - padding,
                right: window.innerWidth - rect.right - padding,
            };
            const fits = {
                top: available.top >= height + 18,
                bottom: available.bottom >= height + 18,
                left: available.left >= width + 18,
                right: available.right >= width + 18,
            };

            if (preferred && fits[preferred]) {
                return preferred;
            }

            return Object.entries(available)
                .sort((left, right) => right[1] - left[1])
                .map(([name]) => name)
                .find((name) => fits[name]) || preferred || "bottom";
        };

        function positionGuide() {
            if (!guideOpen || !activeGuideTarget) {
                return;
            }

            if (isMobileGuide()) {
                guide.dataset.mobile = "true";
                guide.dataset.placement = "bottom";
                guide.style.top = "auto";
                guide.style.left = "0.75rem";
                return;
            }

            guide.dataset.mobile = "false";

            const rect = activeGuideTarget.getBoundingClientRect();
            const bubbleRect = guide.getBoundingClientRect();
            const bubbleWidth = bubbleRect.width || Math.min(340, window.innerWidth - 24);
            const bubbleHeight = bubbleRect.height || 220;
            const viewportPadding = 16;
            const isHeroIntro = activeGuideTarget.classList.contains("terra-guide-floating-anchor");

            if (isHeroIntro) {
                const heroRect = activeGuideTarget.closest(".terra-hero")?.getBoundingClientRect() || rect;
                const centeredLeft = clamp(
                    heroRect.left + (heroRect.width - bubbleWidth) / 2,
                    viewportPadding,
                    window.innerWidth - bubbleWidth - viewportPadding,
                );
                const centeredTop = clamp(
                    heroRect.top + (heroRect.height - bubbleHeight) / 2,
                    viewportPadding,
                    window.innerHeight - bubbleHeight - viewportPadding,
                );

                guide.dataset.placement = "center";
                guide.style.left = `${Math.round(centeredLeft)}px`;
                guide.style.top = `${Math.round(centeredTop)}px`;
                return;
            }

            const placement = pickPlacement(guideAnchors[activeGuideIndex]?.placement, rect, bubbleWidth, bubbleHeight);
            const spacing = 18;
            let top = rect.bottom + spacing;
            let left = rect.left;

            if (placement === "top") {
                top = rect.top - bubbleHeight - spacing;
                left = rect.left;
            } else if (placement === "left") {
                top = rect.top + (rect.height - bubbleHeight) / 2;
                left = rect.left - bubbleWidth - spacing;
            } else if (placement === "right") {
                top = rect.top + (rect.height - bubbleHeight) / 2;
                left = rect.right + spacing;
            }

            if (placement === "top" || placement === "bottom") {
                left = clamp(left, viewportPadding, window.innerWidth - bubbleWidth - viewportPadding);
            }

            if (placement === "left" || placement === "right") {
                top = clamp(top, viewportPadding, window.innerHeight - bubbleHeight - viewportPadding);
            }

            guide.dataset.placement = placement;
            guide.style.left = `${Math.round(left)}px`;
            guide.style.top = `${Math.round(clamp(top, viewportPadding, window.innerHeight - bubbleHeight - viewportPadding))}px`;
        }

        const syncGuideStep = (index, options = {}) => {
            const { remember = false } = options;
            const guideStep = guideAnchors[index];
            if (!guideStep) {
                return;
            }

            activeGuideIndex = index;
            clearGuideTarget();
            activeGuideTarget = guideStep.element;
            activeGuideTarget.classList.add("guide-focus-target");
            if (activeGuideTarget.classList.contains("terra-guide-floating-anchor")) {
                body.classList.add("guide-hero-intro-active");
            }

            const targetRect = activeGuideTarget.getBoundingClientRect();
            const targetIsVisible = targetRect.top >= 110 && targetRect.bottom <= window.innerHeight - 80;
            if (!targetIsVisible) {
                activeGuideTarget.scrollIntoView({
                    block: isMobileGuide() ? "start" : "center",
                    inline: "nearest",
                    behavior: reduceMotion.matches ? "auto" : "smooth",
                });
            }

            if (guideAvatar) {
                guideAvatar.textContent = guideStep.emoji;
            }
            if (guideTitle) {
                guideTitle.textContent = guideStep.title;
            }
            if (guideText) {
                guideText.textContent = guideStep.text;
            }
            if (guideProgress) {
                guideProgress.textContent = `${index + 1} / ${guideAnchors.length}`;
            }
            if (guideNext) {
                guideNext.textContent = index === guideAnchors.length - 1 ? "Готово" : "Дальше";
            }

            body.classList.add("guide-overlay-active");
            guideOpen = true;
            guide.setAttribute("aria-hidden", "false");
            launcher.classList.add("d-none");

            window.setTimeout(() => {
                positionGuide();
                guide.classList.add("is-open");
            }, targetIsVisible || reduceMotion.matches ? 40 : 280);

            if (remember) {
                safeStorage.set(storageKey, "0");
            }
        };

        const closeGuide = ({ remember = true } = {}) => {
            guideOpen = false;
            guide.classList.remove("is-open");
            guide.setAttribute("aria-hidden", "true");
            clearGuideTarget();
            launcher.classList.remove("d-none");
            if (remember) {
                safeStorage.set(storageKey, "1");
            }
        };

        launcher.addEventListener("click", () => {
            safeStorage.set(storageKey, "0");
            syncGuideStep(0, { remember: true });
        });

        guideNext?.addEventListener("click", () => {
            if (activeGuideIndex >= guideAnchors.length - 1) {
                closeGuide();
                return;
            }
            syncGuideStep(activeGuideIndex + 1);
        });

        guideDismiss?.addEventListener("click", () => closeGuide());
        guideClose?.addEventListener("click", () => closeGuide());

        window.addEventListener("resize", queueGuidePosition);
        window.addEventListener("scroll", queueGuidePosition, { passive: true });

        if (safeStorage.get(storageKey) !== "1") {
            window.setTimeout(() => {
                syncGuideStep(0);
            }, reduceMotion.matches ? 120 : 700);
        }
    }
});
