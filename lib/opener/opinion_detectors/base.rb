require 'open3'

require_relative 'base/version'

module Opener
  module OpinionDetectors
    ##
    # The base Opinion detector that supports English and Dutch.
    #
    # @!attribute [r] args
    #  @return [Array]
    # @!attribute [r] options
    #  @return [Hash]
    #
    class Base
      attr_reader :args, :options

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
        return "python -E -O #{kernel} #{args.join(' ')}"
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
        return File.join(core_dir, 'opinion_miner_crfsuite.py')
      end
    end # Base
    
    class EN < Base
    end # EN
    
    class NL < Base
    end # NL
    
  end # OpinionDetectors
end # Opener
