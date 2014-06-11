require 'erb'
require 'tempfile'

module Opener
  module OpinionDetectors
    class ConfigurationCreator
      attr_reader :language, :domain
      attr_accessor :config_file

      include ERB::Util

      def initialize(language, domain, models_path)
        @language = language
        @domain = domain
        @models_path = models_path ||= ENV["OPINION_DETECTOR_MODELS_PATH"]
        @config_file = Tempfile.new('opinion-detector-config')
      end

      def config_file_path
        config_file.write(render)

        return config_file.path
      end
      
      def close_config
        config_file.close
      end

      def render
        ERB.new(template).result(binding)
      end

      def models_path
        if @models_path.nil?
          raise ArgumentError, "Can't find a models path, please set the OPINION_DETECTOR_MODELS_PATH env variable"
        end
        path = File.expand_path(language, @models_path)
        return path
      end

      def crfsuite_path
        File.expand_path("../../../../core/vendor/build/bin/crfsuite",__FILE__)
      end

      def svm_learn_path
        File.expand_path("../../../../core/vendor/build/bin/svm_learn", __FILE__)
      end

      def svm_classify_path
        File.expand_path("../../../../core/vendor/build/bin/svm_classify", __FILE__)
      end

      def template
        %{
[general]
output_folder = <%=models_path%>/<%=domain%>_cfg1

[feature_templates]
expression = <%=models_path%>/<%=domain%>_cfg1/feature_templates/feat_template_expr.txt
holder = <%=models_path%>/<%=domain%>_cfg1/feature_templates/feat_template_holder.txt
target = <%=models_path%>/<%=domain%>_cfg1/feature_templates/feat_template_target.txt

[valid_opinions]
negative = Negative;StrongNegative
positive = Positive;StrongPositive

[relation_features]
use_dependencies = True
use_training_lexicons = True
use_this_expression_lexicon = <%=models_path%>/<%=domain%>_cfg1/lexicons/polarity_lexicon.txt
use_this_target_lexicon = <%=models_path%>/<%=domain%>_cfg1/lexicons/target_lexicon.txt
use_tokens_lemmas = True
exp_tar_threshold = -0.75
exp_hol_threshold = -0.5

[crfsuite]
path_to_binary = <%= crfsuite_path %>
parameters = -a lbfgs

[svmlight]
path_to_binary_learn = <%= svm_learn_path %>
path_to_binary_classify = <%= svm_classify_path %>
parameters = -c 0.1
        }
      end

    end
  end
end
