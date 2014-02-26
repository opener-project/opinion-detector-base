require 'open3'
require 'erb'
require 'tempfile'

require_relative 'base/version'

module Opener
  module OpinionDetectors
    class ModelsMissing < StandardError; end

    ##
    # The base Opinion detector that supports English and Dutch.
    #
    # @!attribute [r] args
    #  @return [Array]
    # @!attribute [r] options
    #  @return [Hash]
    #
    class Base
      attr_reader :args, :options, :conf_file

      def initialize(options = {})
        @args          = options.delete(:args) || []
        @options       = options
        @conf_file = ConfigurationCreator.new.config_file_path
      end

      ##
      # Builds the command used to execute the kernel.
      #
      # @param [Array] args Commandline arguments passed to the command.
      #
      def command
        return "python -E -OO #{kernel} #{conf_file.path} #{args.join(' ')}"
      end

      ##
      # Runs the command and returns the output of STDOUT, STDERR and the
      # process information.
      #
      # @param [String] input The input to tag.
      # @return [Array]
      #
      def run(input)
        return Open3.capture3(command, :stdin_data => input)
      end

      protected

      ##
      # @return [String]
      #
      def core_dir
        return File.expand_path('../../../../core', __FILE__)
      end

      ##
      # @return [String]
      #
      def kernel
        return File.join(core_dir, 'python-scripts/classify_kaf_naf_file.py')
      end

    end # Base


    class EN < Base
    end # EN

    class NL < Base
    end # NL

    class ConfigurationCreator
      include ERB::Util

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
        return env_path unless env_path.nil?

        raise ModelsMissing, "Please provide an environment variable named
          OPINION_DETECTOR_MODELS_PATH that contains the path to the models"
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

      def get_binding
        binding
      end

    end
  end # OpinionDetectors
end # Opener
