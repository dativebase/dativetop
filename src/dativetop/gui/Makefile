export HERE = $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

run-repl:  ## Run DativeTop GUI in development and start a REPL connected to the browser. Uses tmux.
	tmux new-session \; \
		send-keys 'yarn shadow-cljs watch app' C-m \; \
		split-window -h \; \
		send-keys 'yarn shadow-cljs cljs-repl app' \;

help:  ## Print this help message.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
