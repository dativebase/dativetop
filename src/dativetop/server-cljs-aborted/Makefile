export HERE = $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

dash:  ## Create a DativeTop Server dashboard
	tmux new-session \; \
		send-keys 'yarn shadow-cljs watch app' C-m \; \
		split-window -h \; \
		send-keys 'node target/main.js' \; \
		split-window -v \; \
		send-keys 'yarn shadow-cljs cljs-repl app' \; \

help:  ## Print this help message.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help

