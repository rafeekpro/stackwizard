#!/usr/bin/env node

import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import fs from 'fs-extra';
import path from 'path';
import os from 'os';
import {
  ErrorCodes,
  StackWizardError,
  ErrorMessages,
  Logger,
  ErrorHandler,
  Validators,
  checkSystemRequirements,
  cleanup,
  isPortAvailable,
  getSystemInfo,
  formatBytes,
  createErrorContext
} from '../src/errors.js';

describe('Error Handling System', () => {
  let testDir;
  let logger;
  let errorHandler;
  
  beforeEach(() => {
    testDir = path.join(os.tmpdir(), `stackwizard-test-${Date.now()}`);
    fs.ensureDirSync(testDir);
    logger = new Logger(true);
    errorHandler = new ErrorHandler(logger);
  });
  
  afterEach(() => {
    if (fs.existsSync(testDir)) {
      fs.removeSync(testDir);
    }
  });
  
  describe('StackWizardError', () => {
    it('should create error with correct properties', () => {
      const error = new StackWizardError(
        ErrorCodes.DIR_EXISTS,
        'Directory exists',
        { path: '/test/path' }
      );
      
      expect(error.code).toBe(ErrorCodes.DIR_EXISTS);
      expect(error.message).toBe('Directory exists');
      expect(error.details).toEqual({ path: '/test/path' });
      expect(error.timestamp).toBeDefined();
    });
  });
  
  describe('Validators', () => {
    describe('projectName', () => {
      it('should accept valid project names', () => {
        expect(Validators.projectName('my-project')).toBe(true);
        expect(Validators.projectName('project123')).toBe(true);
        expect(Validators.projectName('test-app-2023')).toBe(true);
      });
      
      it('should reject invalid project names', () => {
        expect(Validators.projectName('')).toContain('cannot be empty');
        expect(Validators.projectName('My-Project')).toContain('lowercase');
        expect(Validators.projectName('-project')).toContain('cannot start');
        expect(Validators.projectName('project-')).toContain('cannot end');
        expect(Validators.projectName('node_modules')).toContain('reserved');
        expect(Validators.projectName('a'.repeat(51))).toContain('too long');
        expect(Validators.projectName('project--name')).toContain('consecutive hyphens');
      });
    });
    
    describe('port', () => {
      it('should accept valid ports', () => {
        expect(Validators.port('3000')).toBe(true);
        expect(Validators.port('8080')).toBe(true);
        expect(Validators.port('65535')).toBe(true);
      });
      
      it('should reject invalid ports', () => {
        expect(Validators.port('abc')).toContain('must be a number');
        expect(Validators.port('0')).toContain('between 1 and 65535');
        expect(Validators.port('65536')).toContain('between 1 and 65535');
        expect(Validators.port('80')).toContain('commonly used');
        expect(Validators.port('3306')).toContain('commonly used');
      });
    });
    
    describe('databaseName', () => {
      it('should accept valid database names', () => {
        expect(Validators.databaseName('my_database')).toBe(true);
        expect(Validators.databaseName('db_2023')).toBe(true);
        expect(Validators.databaseName('test_db')).toBe(true);
      });
      
      it('should reject invalid database names', () => {
        expect(Validators.databaseName('')).toContain('cannot be empty');
        expect(Validators.databaseName('My-Database')).toContain('lowercase');
        expect(Validators.databaseName('_database')).toContain('cannot start');
        expect(Validators.databaseName('database_')).toContain('cannot end');
      });
    });
    
    describe('databasePassword', () => {
      it('should accept valid passwords', () => {
        expect(Validators.databasePassword('password123')).toBe(true);
        expect(Validators.databasePassword('verysecurepassword')).toBe(true);
      });
      
      it('should reject invalid passwords', () => {
        expect(Validators.databasePassword('')).toContain('cannot be empty');
        expect(Validators.databasePassword('short')).toContain('at least 8 characters');
      });
    });
  });
  
  describe('Logger', () => {
    it('should create log file in debug mode', () => {
      const debugLogger = new Logger(true);
      expect(debugLogger.logFile).toBeDefined();
      expect(debugLogger.debugMode).toBe(true);
    });
    
    it('should not create log file when not in debug mode', () => {
      const normalLogger = new Logger(false);
      expect(normalLogger.logFile).toBeNull();
      expect(normalLogger.debugMode).toBe(false);
    });
    
    it('should log messages at different levels', () => {
      logger.debug('Debug message', { data: 'test' });
      logger.info('Info message');
      logger.warn('Warning message');
      logger.error('Error message', new Error('Test error'));
      
      // Check that log file exists and contains content
      if (logger.logFile) {
        expect(fs.existsSync(logger.logFile)).toBe(true);
        const logContent = fs.readFileSync(logger.logFile, 'utf8');
        expect(logContent).toContain('Debug message');
        expect(logContent).toContain('Info message');
        expect(logContent).toContain('Warning message');
        expect(logContent).toContain('Error message');
      }
    });
  });
  
  describe('ErrorHandler', () => {
    it('should handle StackWizardError correctly', async () => {
      const error = new StackWizardError(
        ErrorCodes.DIR_EXISTS,
        'Directory already exists',
        { path: '/test/path' }
      );
      
      const result = await errorHandler.handle(error, {
        projectName: 'test-project'
      });
      
      expect(result).toBe(true); // DIR_EXISTS is recoverable
      expect(errorHandler.errorCount).toBe(1);
    });
    
    it('should determine error codes from system errors', () => {
      const eexistError = new Error('EEXIST: file already exists');
      eexistError.code = 'EEXIST';
      expect(errorHandler.determineErrorCode(eexistError)).toBe(ErrorCodes.DIR_EXISTS);
      
      const eaccessError = new Error('EACCES: permission denied');
      eaccessError.code = 'EACCES';
      expect(errorHandler.determineErrorCode(eaccessError)).toBe(ErrorCodes.PERMISSION_DENIED);
      
      const enospcError = new Error('ENOSPC: no space left on device');
      enospcError.code = 'ENOSPC';
      expect(errorHandler.determineErrorCode(enospcError)).toBe(ErrorCodes.DISK_FULL);
    });
    
    it('should track recovery attempts', async () => {
      const error = new StackWizardError(
        ErrorCodes.NETWORK_ERROR,
        'Network connection failed'
      );
      
      // First attempt
      await errorHandler.handle(error, { projectName: 'test' });
      expect(errorHandler.recoveryAttempts['NETWORK_ERROR_test']).toBe(1);
      
      // Second attempt
      await errorHandler.handle(error, { projectName: 'test' });
      expect(errorHandler.recoveryAttempts['NETWORK_ERROR_test']).toBe(2);
      
      // Third attempt
      await errorHandler.handle(error, { projectName: 'test' });
      expect(errorHandler.recoveryAttempts['NETWORK_ERROR_test']).toBe(3);
      
      // Fourth attempt should not recover (max attempts reached)
      const result = await errorHandler.handle(error, { projectName: 'test' });
      expect(result).toBe(false);
    });
    
    it('should generate error report', () => {
      errorHandler.generateErrorReport();
      
      const reportPath = path.join(os.homedir(), '.stackwizard', 'error-report.json');
      if (fs.existsSync(reportPath)) {
        const report = fs.readJsonSync(reportPath);
        expect(report.timestamp).toBeDefined();
        expect(report.platform).toBe(process.platform);
        expect(report.nodeVersion).toBe(process.version);
        expect(report.errorCount).toBeDefined();
      }
    });
  });
  
  describe('System Requirements', () => {
    it('should check for required tools', async () => {
      try {
        const requirements = await checkSystemRequirements(logger);
        
        // Node and npm should always be installed
        expect(requirements.node.installed).toBe(true);
        expect(requirements.npm.installed).toBe(true);
        
        // Check version information
        expect(requirements.node.version).toBeDefined();
        expect(requirements.npm.version).toBeDefined();
      } catch (error) {
        // If requirements fail, it should be a StackWizardError
        expect(error).toBeInstanceOf(StackWizardError);
      }
    });
  });
  
  describe('Port Availability', () => {
    it('should detect available ports', async () => {
      // High port numbers are likely to be available
      const available = await isPortAvailable(54321);
      expect(typeof available).toBe('boolean');
    });
    
    it('should detect unavailable ports', async () => {
      // Create a server to occupy a port
      const net = await import('net');
      const server = net.createServer();
      
      await new Promise((resolve) => {
        server.listen(54322, '127.0.0.1', resolve);
      });
      
      const available = await isPortAvailable(54322);
      expect(available).toBe(false);
      
      await new Promise((resolve) => {
        server.close(resolve);
      });
    });
  });
  
  describe('Cleanup', () => {
    it('should remove directory on cleanup', async () => {
      const cleanupDir = path.join(testDir, 'cleanup-test');
      fs.ensureDirSync(cleanupDir);
      fs.writeFileSync(path.join(cleanupDir, 'test.txt'), 'test content');
      
      await cleanup(cleanupDir, logger);
      
      expect(fs.existsSync(cleanupDir)).toBe(false);
    });
    
    it('should create backup for large directories', async () => {
      const cleanupDir = path.join(testDir, 'large-cleanup-test');
      fs.ensureDirSync(cleanupDir);
      
      // Create a file larger than 1MB
      const largeContent = 'x'.repeat(1024 * 1024 + 1);
      fs.writeFileSync(path.join(cleanupDir, 'large.txt'), largeContent);
      
      await cleanup(cleanupDir, logger);
      
      expect(fs.existsSync(cleanupDir)).toBe(false);
      // Check if backup was created
      const backupExists = fs.readdirSync(testDir).some(f => f.startsWith('large-cleanup-test.backup-'));
      expect(backupExists).toBe(true);
    });
    
    it('should handle cleanup errors gracefully', async () => {
      const nonExistentDir = path.join(testDir, 'non-existent');
      
      // Should not throw error
      await expect(cleanup(nonExistentDir, logger)).resolves.not.toThrow();
    });
  });
  
  describe('Utility Functions', () => {
    it('should format bytes correctly', () => {
      expect(formatBytes(0)).toBe('0 Bytes');
      expect(formatBytes(1024)).toBe('1 KB');
      expect(formatBytes(1024 * 1024)).toBe('1 MB');
      expect(formatBytes(1024 * 1024 * 1024)).toBe('1 GB');
      expect(formatBytes(1536, 1)).toBe('1.5 KB');
    });
    
    it('should get system information', () => {
      const info = getSystemInfo();
      
      expect(info.platform).toBe(process.platform);
      expect(info.arch).toBe(process.arch);
      expect(info.nodeVersion).toBe(process.version);
      expect(info.memory).toBeDefined();
      expect(info.memory.total).toBeGreaterThan(0);
      expect(info.memory.free).toBeGreaterThan(0);
      expect(info.cpu).toBeDefined();
      expect(info.cpu.cores).toBeGreaterThan(0);
      expect(info.user).toBeDefined();
      expect(info.cwd).toBe(process.cwd());
    });
    
    it('should create error context', () => {
      const error = new Error('Test error');
      error.code = 'TEST_CODE';
      
      const context = createErrorContext(error, { custom: 'data' });
      
      expect(context.error.message).toBe('Test error');
      expect(context.error.code).toBe('TEST_CODE');
      expect(context.system).toBeDefined();
      expect(context.context.custom).toBe('data');
      expect(context.timestamp).toBeDefined();
    });
  });
  
  describe('Error Messages', () => {
    it('should have messages for all error codes', () => {
      Object.values(ErrorCodes).forEach(code => {
        if (code !== 'UNKNOWN_ERROR') {
          const message = ErrorMessages[code];
          expect(message).toBeDefined();
          expect(message.message).toBeDefined();
          expect(message.solution).toBeDefined();
          expect(typeof message.recoverable).toBe('boolean');
        }
      });
    });
  });
});

describe('Integration Tests', () => {
  it('should handle full error flow', async () => {
    const logger = new Logger(true);
    const errorHandler = new ErrorHandler(logger);
    
    // Simulate a directory exists error
    const error = new StackWizardError(
      ErrorCodes.DIR_EXISTS,
      'Project directory already exists',
      { path: '/test/my-project' }
    );
    
    const result = await errorHandler.handle(error, {
      projectName: 'my-project',
      details: 'Path: /test/my-project'
    });
    
    expect(result).toBe(true);
    expect(errorHandler.errorCount).toBe(1);
    
    // Generate error report
    const report = errorHandler.generateErrorReport();
    expect(report.errorCount).toBe(1);
  });
  
  it('should handle cascading errors', async () => {
    const logger = new Logger(true);
    const errorHandler = new ErrorHandler(logger);
    
    // First error: Network error
    const networkError = new StackWizardError(
      ErrorCodes.NETWORK_ERROR,
      'Failed to download dependencies'
    );
    
    await errorHandler.handle(networkError, { projectName: 'test' });
    
    // Second error: NPM install failed
    const npmError = new StackWizardError(
      ErrorCodes.NPM_INSTALL_FAILED,
      'npm install failed'
    );
    
    await errorHandler.handle(npmError, { projectName: 'test' });
    
    expect(errorHandler.errorCount).toBe(2);
  });
});