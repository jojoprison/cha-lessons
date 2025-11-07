.PHONY: help ru th full answers ru3 th3 full3 answers3 deps

UV ?= uv
SCRIPT := build_lesson4_auxiliary_verbs_v1.py
TRS := lesson4_translations_source.txt
SCRIPT3 := build_lesson3_w_questions_v1.py
TRS3 := lesson3_translations_source.txt
ANS3 := lesson3_answers_source.txt

help:
	@echo "Targets:"
	@echo "  make ru    # Генерация только RU (контент: RU; словарь без TH)"
	@echo "  make th    # Генерация только TH (контент: TH; словарь с TH)"
	@echo "  make full  # Генерация RU+TH (контент RU+TH; словарь с TH)"
	@echo "  make answers  # Генерация TH контента + TH словарь + ответы (фиолетовым)"
	@echo "  make ru3   # Урок 3: только RU (контент RU)"
	@echo "  make th3   # Урок 3: только TH (контент TH)"
	@echo "  make full3 # Урок 3: RU+TH (контент RU+TH)"
	@echo "  make answers3 # Урок 3: только TH + ответы (фиолетовым)"
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

answers:
	$(UV) run python $(SCRIPT) \
	  --translations-source $(TRS) \
	  --no-ru --with-th \
	  --vocab-th --no-vocab-ru \
	  --with-answers
	@echo "[make] ANSWERS (TH+vocab TH+answers) build finished"

# -------- Lesson 3 (W-Questions) --------
ru3:
	$(UV) run python $(SCRIPT3) \
	  --translations-source $(TRS3) \
	  --with-ru --no-th
	@echo "[make] Lesson3 RU build finished"

th3:
	$(UV) run python $(SCRIPT3) \
	  --translations-source $(TRS3) \
	  --no-ru --with-th
	@echo "[make] Lesson3 TH build finished"

full3:
	$(UV) run python $(SCRIPT3) \
	  --translations-source $(TRS3) \
	  --with-ru --with-th
	@echo "[make] Lesson3 FULL build finished"

answers3:
	$(UV) run python $(SCRIPT3) \
	  --translations-source $(TRS3) \
	  --no-ru --with-th \
	  --with-answers \
	  --answers-source $(ANS3)
	@echo "[make] Lesson3 ANSWERS (TH+answers) build finished"
