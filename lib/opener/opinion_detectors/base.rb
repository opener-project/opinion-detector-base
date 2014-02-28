require 'open3'

require_relative 'base/version'
require_relative 'configuration_creator'
require_relative 'en'
require_relative 'nl'

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
        return "#{adjust_python_path} python -E -OO #{kernel} #{conf_file.path} #{args.join(' ')}"
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
      def adjust_python_path
        site_packages =  File.join(core_dir, 'site-packages')
        "env PYTHONPATH=#{site_packages}:$PYTHONPATH"
      end


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
  end # OpinionDetectors
end # Opener
