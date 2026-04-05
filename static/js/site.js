document.addEventListener("DOMContentLoaded", () => {
    const phoneInputs = document.querySelectorAll("[data-phone-input='true']");

    const getPhoneDigits = (value, maxDigits) => {
        let digits = String(value || "").replace(/\D/g, "");
        if (digits.length === maxDigits + 1 && /^[78]/.test(digits)) {
            digits = digits.slice(1);
        }
        return digits.slice(0, maxDigits);
    };

    const formatPhoneValue = (digits) => {
        if (!digits) {
            return "";
        }

        const parts = [];
        const area = digits.slice(0, 3);
        const first = digits.slice(3, 6);
        const second = digits.slice(6, 8);
        const third = digits.slice(8, 10);

        if (area) {
            parts.push(`(${area}`);
        }
        if (area.length === 3) {
            parts[0] += ")";
        }
        if (first) {
            parts.push(first);
        }
        if (second) {
            parts.push(second);
        }
        if (third) {
            parts.push(third);
        }

        const formatted = [];
        if (parts[0]) {
            formatted.push(parts[0]);
        }
        if (parts[1]) {
            formatted.push(parts[1]);
        }
        let result = formatted.join(" ");
        if (parts[2]) {
            result += `-${parts[2]}`;
        }
        if (parts[3]) {
            result += `-${parts[3]}`;
        }
        return result;
    };

    const applyPhoneFormatting = (input) => {
        const maxDigits = Number(input.dataset.phoneDigits || 10);
        const digits = getPhoneDigits(input.value, maxDigits);
        input.value = formatPhoneValue(digits);

        if (digits.length && digits.length < maxDigits) {
            input.setCustomValidity(`Введите ${maxDigits} цифр номера телефона.`);
        } else {
            input.setCustomValidity("");
        }
    };

    phoneInputs.forEach((input) => {
        applyPhoneFormatting(input);
        input.addEventListener("input", () => applyPhoneFormatting(input));
        input.addEventListener("blur", () => applyPhoneFormatting(input));
        input.addEventListener("paste", () => {
            window.requestAnimationFrame(() => applyPhoneFormatting(input));
        });
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
    [...popoverTriggerList].forEach((element) => new bootstrap.Popover(element));

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
        slider.addEventListener("keydown", (event) => {
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
            const isValid = form.checkValidity();
            if (!isValid) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add("was-validated");
        });
    });

    const pricingConfigElement = document.getElementById("brief-pricing-config");
    const briefForm = document.querySelector("[data-brief-pricing]");
    if (pricingConfigElement && briefForm) {
        const pricingConfig = JSON.parse(pricingConfigElement.textContent);
        const clientTypeField = document.getElementById("id_client_type");
        const businessNameLabel = document.getElementById("business-name-label");
        const businessNameInput = document.getElementById("id_business_name");
        const siteTypeField = document.getElementById("id_site_type");
        const hostingField = document.getElementById("id_need_hosting");
        const domainField = document.getElementById("id_need_domain");
        const estimatedPriceField = document.getElementById("id_estimated_price");
        const summaryService = document.querySelector("[data-summary-service]");
        const summaryBase = document.querySelector("[data-summary-base]");
        const summaryTotal = document.querySelector("[data-summary-total]");

        const formatRub = (value) =>
            `${Math.round(Number(value || 0)).toLocaleString("ru-RU")} ₽`;

        const updateBusinessNameLabel = () => {
            if (!clientTypeField || !businessNameLabel || !businessNameInput) {
                return;
            }
            const isLegalEntity = clientTypeField.value === "legal_entity";
            businessNameLabel.textContent = isLegalEntity ? "Наименование компании" : "Имя";
            businessNameInput.placeholder = isLegalEntity ? "ООО Ромашка" : "Иван Иванов";
        };

        const updatePricing = () => {
            if (!siteTypeField || !summaryService || !summaryBase || !summaryTotal) {
                return;
            }
            const basePrice = Number(pricingConfig.site_type_prices[siteTypeField.value] || 0);
            const hostingPrice = hostingField && hostingField.checked ? Number(pricingConfig.hosting_price || 0) : 0;
            const domainPrice = domainField && domainField.checked ? Number(pricingConfig.domain_price || 0) : 0;
            const total = basePrice + hostingPrice + domainPrice;

            summaryService.textContent = siteTypeField.options[siteTypeField.selectedIndex]?.text || "";
            summaryBase.textContent = formatRub(basePrice);
            summaryTotal.textContent = formatRub(total);
            if (estimatedPriceField) {
                estimatedPriceField.value = total.toFixed(2);
            }
        };

        updateBusinessNameLabel();
        updatePricing();

        clientTypeField?.addEventListener("change", updateBusinessNameLabel);
        siteTypeField?.addEventListener("change", updatePricing);
        hostingField?.addEventListener("change", updatePricing);
        domainField?.addEventListener("change", updatePricing);
    }
});
