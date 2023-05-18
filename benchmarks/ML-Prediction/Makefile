HOME_DIR = /home/kingdo
OPENWHISK_PROJECT_HOME ?= $(HOME_DIR)/IdeaProjects/openwhisk
WSK_CLI ?= $(OPENWHISK_PROJECT_HOME)/bin/wsk
WSK_CONFIG_FILE=$(HOME_DIR)/.wskprops

FAASTLANE_PROJECT_HOME ?= $(HOME_DIR)/PycharmProjects/faastlane
FAASTLANE_WORK_DIR ?= $(CURDIR)/.faastlane

DOCKER_IMAGE = kingdo/action-python-v3.10
DOCKER_IMAGE_TAG = latest

# #####################################################################################################
# For Faastlane

Faastlane_ACTION_NAME = ML-Prediction-Faastlane

BUILD_MODE ?= PURE_PYTHON_FILE
ifeq ("$(BUILD_MODE)","PURE_PYTHON_FILE")
	ACTION_ZIP = ML-Prediction.zip
else
	ACTION_ZIP = ML-Prediction-Virtualenv.zip
endif

__main__.py: predict.py render.py resize.py workflow.json
	FAASTLANE_WORK_DIR=$(FAASTLANE_WORK_DIR) python3 $(FAASTLANE_PROJECT_HOME)/composer/generator.py --input . --platform ow
	cp $(FAASTLANE_WORK_DIR)/__main__.py __main__.py
.PHONY: generate-faastlane-runner
generate-faastlane-runner: __main__.py

virtualenv: __main__.py data
	docker run --rm -v ".:/src" --entrypoint bash $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) \
      -c "mkdir /ttt /tt && cp -r /src/* /ttt && compile main /ttt /tt && mv /tt/virtualenv /src/ && exit"
.PHONY: create-virtualenv
create-virtualenv: virtualenv

ML-Prediction-Virtualenv.zip:
	zip -r ML-Prediction virtualenv requirements.txt data __main__.py resize.py predict.py render.py
.PHONY: pack-virtualenv-action
pack-virtualenv-action: ML-Prediction-Virtualenv.zip

ML-Prediction.zip: __main__.py data
	zip -r ML-Prediction data __main__.py resize.py predict.py render.py
.PHONY: pack-action
pack-action: ML-Prediction.zip

.faastlane_action_is_deployed: $(ACTION_ZIP)
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update $(Faastlane_ACTION_NAME) $(ACTION_ZIP) \
		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 10240 -t 300000
	touch .faastlane_action_is_deployed

action_invoke_Faastlane: .faastlane_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result $(Faastlane_ACTION_NAME) --param op FT


# #####################################################################################################
# For Faastorage, OFC and Openwhisk

.resize_action_is_deployed: data resize.py
	cp resize.py __main__.py && zip -r resize_action data __main__.py && rm __main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update ML-Prediction-Three-resize resize_action.zip \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch .resize_action_is_deployed
.PHONY: resize_action_invoke
resize_action_invoke: .resize_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result ML-Prediction-Three-resize --param op OW


.predict_action_is_deployed: predict.py
	cp predict.py __main__.py && zip -r predict_action data __main__.py && rm __main__.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update ML-Prediction-Three-predict predict_action.zip \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 10240 -t 300000
	touch .predict_action_is_deployed
.PHONY: predict_action_invoke
predict_action_invoke: .predict_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result ML-Prediction-Three-predict --param op OW


.render_action_is_deployed: render.py
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update ML-Prediction-Three-render render.py \
    		--docker $(DOCKER_IMAGE):$(DOCKER_IMAGE_TAG) -m 1024 -t 300000
	touch .render_action_is_deployed
.PHONY: render_action_invoke
render_action_invoke: .render_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result ML-Prediction-Three-render --param op OW


.sequence_action_is_deployed: .resize_action_is_deployed .predict_action_is_deployed .render_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action update ML-Prediction-Three-sequence --sequence ML-Prediction-Three-resize,ML-Prediction-Three-predict,ML-Prediction-Three-render
	touch .sequence_action_is_deployed

action_invoke_OFC: .sequence_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result ML-Prediction-Three-sequence --param op OFC

action_invoke_Faastorage: .sequence_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result ML-Prediction-Three-sequence --param op CB

action_invoke_Openwhisk: .sequence_action_is_deployed
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action invoke --result ML-Prediction-Three-sequence --param op OW

clean:
	rm -rf .sequence_action_is_deployed .resize_action_is_deployed .predict_action_is_deployed .render_action_is_deployed .faastlane_action_is_deployed
	rm -rf __main__.py .faastlane
	# rm -rf result-*
	rm -rf predict_action.zip resize_action.zip $(ACTION_ZIP)
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete ML-Prediction-Three-sequence
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete ML-Prediction-Three-render
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete ML-Prediction-Three-predict
	WSK_CONFIG_FILE=$(WSK_CONFIG_FILE) $(WSK_CLI) -i action delete ML-Prediction-Three-resize
