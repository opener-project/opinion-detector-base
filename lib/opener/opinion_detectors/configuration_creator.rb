require 'erb'
require 'tempfile'

module Opener
  module OpinionDetectors
    class ConfigurationCreator
      attr_reader :language

      include ERB::Util

      def initialize(language)
        @language = language
      end

      def config_file_path
        file = Tempfile.new('opinion-detector-config')
        file.write(render)
        file.close

        return file
      end

      def render
        ERB.new(template).result(binding)
      end

      def models_path
        env_path = ENV["OPINION_DETECTOR_MODELS_PATH"]
        if env_path.nil?
          raise ModelsMissing, "Please provide an environment variable named
            OPINION_DETECTOR_MODELS_PATH that contains the path to the models"
        end

        path = File.expand_path("hotel_#{language}", env_path)
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
output_folder = <%=models_path%>

[crfsuite]
path_to_binary = <%= crfsuite_path %>

[svmlight]
path_to_binary_learn = <%= svm_learn_path %>
path_to_binary_classify = <%= svm_classify_path %>
        }
      end

    end
  end
end
