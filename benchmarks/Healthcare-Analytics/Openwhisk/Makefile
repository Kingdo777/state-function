HOME_DIR = /home/kingdo
OPENWHISK_PROJECT_HOME ?= $(HOME_DIR)/IdeaProjects/openwhisk
WSK_CLI ?= $(OPENWHISK_PROJECT_HOME)/bin/wsk
WSK_CONFIG_FILE=$(HOME_DIR)/.wskprops

DOCKER_IMAGE = kingdo/action-python-v3.10
DOCKER_IMAGE_TAG = latest


identifyphi/.identifyphi_action_is_deployed: identifyphi/__main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update Healthcare-Analytics-identifyphi identifyphi/__main__.py \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch identifyphi/.identifyphi_action_is_deployed
.PHONY: identifyphi_action_invoke
identifyphi_action_invoke: identifyphi/.identifyphi_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result Healthcare-Analytics-identifyphi --param-file identifyphi/param.json


anonymize/.anonymize_action_is_deployed: anonymize/__main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update Healthcare-Analytics-anonymize anonymize/__main__.py \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch anonymize/.anonymize_action_is_deployed
.PHONY: anonymize_action_invoke
anonymize_action_invoke: anonymize/.anonymize_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result Healthcare-Analytics-anonymize --param-file anonymize/param.json


analytics/.analytics_action_is_deployed: analytics/__main__.py
	cd analytics && zip -r analytics_action nltk_data __main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update Healthcare-Analytics-analytics analytics/analytics_action.zip \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch analytics/.analytics_action_is_deployed
.PHONY: analytics_action_invoke
analytics_action_invoke: analytics/.analytics_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result Healthcare-Analytics-analytics --param-file analytics/param.json


.sequence_action_is_deployed: identifyphi/.identifyphi_action_is_deployed anonymize/.anonymize_action_is_deployed analytics/.analytics_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update Healthcare-Analytics-sequence --sequence Healthcare-Analytics-identifyphi,Healthcare-Analytics-anonymize,Healthcare-Analytics-analytics
	touch .sequence_action_is_deployed

sequence_action_invoke: .sequence_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result Healthcare-Analytics-sequence --param-file identifyphi/param.json

clean:
	rm -rf .sequence_action_is_deployed identifyphi/.identifyphi_action_is_deployed anonymize/.anonymize_action_is_deployed analytics/.analytics_action_is_deployed
	rm -rf analytics/analytics_action.zip
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete Healthcare-Analytics-sequence
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete Healthcare-Analytics-analytics
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete Healthcare-Analytics-anonymize
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete Healthcare-Analytics-identifyphi