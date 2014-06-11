require 'nokogiri'
require 'open3'

require_relative 'base/version'
require_relative 'configuration_creator'
require_relative 'en'
require_relative 'nl'
require_relative 'de'
require_relative 'it'
require_relative 'fr'
require_relative 'es'

module Opener
  module OpinionDetectors
    class ModelsMissing < StandardError; end

    ##
    # The base Opinion detector that supports English and Dutch.
    #
    # @!attribute [r] args
    #  @return [Array]
    #
    # @!attribute [r] options
    #  @return [Hash]
    #
    class Base
      attr_reader :args, :options

      ##
      # Hash containing the default options to use.
      #
      # @return [Hash]
      #
      DEFAULT_OPTIONS = {
        :domain => "hotel"
      }.freeze

      ##
      # @param [Hash] options
      #
      # @option options [Array] :args Extra commandline arguments to use.
      #
      def initialize(options = {})
        @args    = options.delete(:args) || []
        @options = DEFAULT_OPTIONS.merge(options)
      end

      ##
      # Builds the command used to execute the kernel.
      #
      # @param [Array] args Commandline arguments passed to the command.
      #
      def command(config_file)
        return "#{adjust_python_path} python -OO #{kernel} -m #{config_file} #{args.join(' ')}"
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
        conf     = ConfigurationCreator.new(
          language,
          options[:domain],
          options[:resource_path]
        )
        stdout, stderr, process = capture(conf.config_file_path, input)
        conf.close_config
        
        
        return stdout, stderr, process
      end

      protected

      ##
      # @return [String]
      #
      def adjust_python_path
        site_packages =  File.join(core_dir, 'site-packages/pre_install')

        return "env PYTHONPATH=#{site_packages}:$PYTHONPATH"
      end

      ##
      # capture3 method doesn't work properly with Jruby, so this is a
      # workaround
      #
      def capture(config_file, input)
        return Open3.popen3(*command(config_file).split(" ")) {|i, o, e, t|
          out_reader = Thread.new { o.read }
          err_reader = Thread.new { e.read }
          i.write input
          i.close
          [out_reader.value, err_reader.value, t.value]
        }
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
