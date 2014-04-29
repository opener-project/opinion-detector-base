require 'nokogiri'
require 'open3'

require_relative 'base/version'
require_relative 'configuration_creator'
require_relative 'en'
require_relative 'nl'
require_relative 'de'
require_relative 'it'

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
        language = language(input)
        @conf_file = ConfigurationCreator.new(language).config_file_path
        return Open3.capture3(*command.split(" "), :stdin_data => input)
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

      ##
      # @return the language from the KAF
      #
      def language(input)
        document = Nokogiri::XML(input)
        language = document.at('KAF').attr('xml:lang')
        return language
      end

    end # Base
  end # OpinionDetectors
end # Opener
