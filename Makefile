.PHONY: help ru th full deps

UV ?= uv
SCRIPT := build_lesson4_auxiliary_verbs_v1.py
TRS := lesson4_translations_source.txt

help:
	@echo "Targets:"
	@echo "  make ru    # Генерация только RU (контент: RU; словарь без TH)"
	@echo "  make th    # Генерация только TH (контент: TH; словарь с TH)"
	@echo "  make full  # Генерация RU+TH (контент RU+TH; словарь с TH)"
	@echo "  make deps  # Установка/синхронизация зависимостей (python-docx)"

deps:
	$(UV) sync

ru:
	$(UV) run python $(SCRIPT) \
	  --translations-source $(TRS) \
	  --with-ru --no-th \
	  --no-vocab-th
	@echo "[make] RU build finished"

th:
	$(UV) run python $(SCRIPT) \
	  --translations-source $(TRS) \
	  --no-ru --with-th \
	  --vocab-th --no-vocab-ru
	@echo "[make] TH build finished"

full:
	$(UV) run python $(SCRIPT) \
	  --translations-source $(TRS) \
	  --with-ru --with-th \
	  --vocab-th --no-vocab-ru
	@echo "[make] FULL build finished"
