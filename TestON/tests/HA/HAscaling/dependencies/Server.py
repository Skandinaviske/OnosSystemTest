"""
Copyright 2016 Open Networking Foundation ( ONF )

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    ( at your option ) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.
"""
"Functions for using the SimpleHTTPServer python module"
import re


class Server():

    def __init__( self ):
        self.default = ''
        self.PID = -1
        self.component = None
        self.rootDir = None

    def __del__( self ):
        self.stop()

    def start( self, component, rootDir, port=8000, logDir=None ):
        """
        Start SimpleHTTPServer as a background process from rootDir on the
        given component. The webserver will listen on port and if specified,
        output will be redirected to logDir.

        Arguments:
        - component = The TestON component handle to start the webserver on
        - rootDir = The root directory for the web content
        - port = The port number for the webserver to listen on. Defaults to 8000
        - logDir = If specified, the output of the webserver will be redirected
                   to this file. Note that this should be either an absolute path
                   or relative to rootDir.
        Returns:
            main.TRUE if the command succedes or main.FALSE if there is an error.
        """
        retValue = main.TRUE
        self.rootDir = rootDir
        try:
            # Save component for this instance so other functions can use it
            self.component = component
            main.log.info( "Starting SimpleHTTPServer on " + component.name )
            if component.handle:
                handle = component.handle
                # cd to rootDir
                handle.sendline( "cd " + str( rootDir ) )
                handle.expect( component.prompt )
                # Start server
                cmd = "python -m SimpleHTTPServer {}".format( port )
                if logDir:
                    cmd += " &> {}".format( logDir )  # pipe all output to a file
                else:
                    cmd += "&> {dev/null}"  # Throw away all output
                cmd += " &"
                handle.sendline( cmd )
                handle.expect( component.prompt )
                response = handle.before
                # Return to home dir
                handle.sendline( "cd " + component.home )
                handle.expect( component.prompt )
                response += handle.before
                if "Exit" in response:
                    main.log.error( "Error starting server. Check server log for details" )
                    main.log.debug( handle.before )
                    # Show the log
                    handle.sendline( "cat {}".format( logDir ))
                    handle.expect( component.prompt )
                    main.log.debug( handle.before )
                    retValue = main.FALSE
                # capture PID for later use
                # EX: [ 1 ] 67987
                match = re.search( "\[\d\] (?P<PID>\d+)", response )
                if match:
                    self.PID = match.group( "PID" )
                else:
                    main.log.warn( "Could not find PID" )
            else:
                main.log.error( "Component handle is not set" )
                retValue = main.FALSE
        except Exception:
            main.log.exception( "Error starting web server" )
            retValue = main.FALSE
        return retValue

    def stop( self ):
        """
        Kills the process of the server. Note that this function must be run
        from the same instance of the server class that the server was started
        on.
        """
        retValue = main.TRUE
        try:
            main.log.info( "Stopping Server." )
            assert self.component, "Component not specified"
            assert self.PID, "PID not found"
            if self.component.handle:
                handle = self.component.handle
                cmd = "sudo kill {}".format( self.PID )
                handle.sendline( cmd )
                handle.expect( component.prompt )
                # TODO: What is bad output? cannot sudo?
            else:
                main.log.error( "Component handle is not set" )
                retValue = main.FALSE
        except Exception:
            main.log.exception( "Error stopping web server" )
            retValue = main.FALSE
        return retValue

    def generateFile( self, nodes, equal=False, filename="cluster.json" ):
        """
        Generate custom metadata file in the root directory using the custom
        onos-gen-partitions file which should also be located in the root
        directory.

        Note that this function needs to be run after the start function has
        been called for this instance.

        Arguments:
        - nodes = The number of ONOS nodes to include in the cluster. Will
                  include nodes in ascending order, I.E. OC1, OC2, etc

        Optional Arguments:
        - equal = Specifies whether all nodes should participate in every
                  partition. Defaults to False.
        - filename = The name of the file to save the cluster metadata to.
                     Defaults to "cluster.json".
        Returns:
            main.TRUE if the command succedes or main.FALSE if there is an error.
        """
        retValue = main.TRUE
        try:
            if self.component.handle:
                assert self.component, "Component not specified. Please start the server first"
                assert self.rootDir, "Root directory not found"
                handle = self.component.handle
                # cd to rootDir
                handle.sendline( "cd " + str( self.rootDir ) )
                handle.expect( component.prompt )
                cmd = "./onos-gen-partitions {} {} ".format( filename, nodes )
                if equal:
                    cmd += "-e"
                handle.sendline( cmd )
                handle.expect( component.prompt )
                response = handle.before
                # Return to home dir
                handle.sendline( "cd " + self.component.home )
                handle.expect( component.prompt )
                response += handle.before
                if "Traceback" in response:
                    main.log.error( handle.before )
                    retValue = main.FALSE
            else:
                main.log.error( "Component handle is not set" )
                retValue = main.FALSE
        except Exception:
            main.log.exception( "Error generating metadata file" )
        return retValue
