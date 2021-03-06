# Copyright 2017 Open Networking Foundation (ONF)
#
# Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
# the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
# or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>
#
#     TestON is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 2 of the License, or
#     (at your option) any later version.
#
#     TestON is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with TestON.  If not, see <http://www.gnu.org/licenses/>.
#
# If you have any questions, or if you don't understand R,
# please contact Jeremy Ronquillo: j_ronquillo@u.pacific.edu

# **********************************************************
# STEP 1: Data management.
# **********************************************************

print( "**********************************************************" )
print( "STEP 1: Data management." )
print( "**********************************************************" )

save_directory = 7

# Command line arguments are read.
print( "Reading commmand-line args." )
args <- commandArgs( trailingOnly=TRUE )

# ----------------
# Import Libraries
# ----------------

print( "Importing libraries." )
library( ggplot2 )
library( reshape2 )
library( RPostgreSQL )    # For databases
source( "~/OnosSystemTest/TestON/JenkinsFile/wikiGraphRScripts/dependencies/saveGraph.R" )
source( "~/OnosSystemTest/TestON/JenkinsFile/wikiGraphRScripts/dependencies/fundamentalGraphData.R" )
source( "~/OnosSystemTest/TestON/JenkinsFile/wikiGraphRScripts/dependencies/initSQL.R" )
source( "~/OnosSystemTest/TestON/JenkinsFile/wikiGraphRScripts/dependencies/cliArgs.R" )

# -------------------
# Check CLI Arguments
# -------------------

print( "Verifying CLI args." )

if ( length( args ) != save_directory ){
    usage( "SCPFhostLat.R" )
    quit( status = 1 )
}

# -----------------
# Create File Names
# -----------------

print( "Creating filenames and title of graph." )

errBarOutputFile <- paste( args[ save_directory ],
                           args[ graph_title ],
                           "_",
                           args[ branch_name ],
                           "_errGraph.jpg",
                           sep="" )

chartTitle <- "Host Latency"
# ------------------
# SQL Initialization
# ------------------

print( "Initializing SQL" )

con <- initSQL( args[ database_host ],
                args[ database_port ],
                args[ database_u_id ],
                args[ database_pw ] )

# ------------------------
# Host Latency SQL Command
# ------------------------

print( "Generating Host Latency SQL Command" )

command  <- paste( "SELECT * FROM host_latency_tests WHERE branch = '",
                   args[ branch_name ],
                   "' AND date IN ( SELECT MAX( date ) FROM host_latency_tests WHERE branch = '",
                   args[ branch_name ],
                   "' ) ",
                   sep = "" )

fileData <- retrieveData( con, command )


# **********************************************************
# STEP 2: Organize data.
# **********************************************************

print( "**********************************************************" )
print( "STEP 2: Organize Data." )
print( "**********************************************************" )

latestBuildDate <- fileData$date[1]

# ------------
# Data Sorting
# ------------

print( "Sorting data." )

requiredColumns <- c( "avg" )

tryCatch( avgs <- c( fileData[ requiredColumns ] ),
          error = function( e ) {
              print( "[ERROR] One or more expected columns are missing from the data. Please check that the data and SQL command are valid, then try again." )
              print( "Required columns: " )
              print( requiredColumns )
              print( "Actual columns: " )
              print( names( fileData ) )
              print( "Error dump:" )
              print( e )
              quit( status = 1 )
          }
         )

# --------------------
# Construct Data Frame
# --------------------

print( "Constructing Data Frame" )

dataFrame <- melt( avgs )
dataFrame$scale <- fileData$scale
dataFrame$std <- fileData$std

colnames( dataFrame ) <- c( "ms",
                            "type",
                            "scale",
                            "std" )

dataFrame <- na.omit( dataFrame )   # Omit any data that doesn't exist

print( "Data Frame Results:" )
print( dataFrame )

# **********************************************************
# STEP 3: Generate graphs.
# **********************************************************

print( "**********************************************************" )
print( "STEP 3: Generate Graph." )
print( "**********************************************************" )

# ------------------
# Generate Main Plot
# ------------------

print( "Creating main plot." )

mainPlot <- ggplot( data = dataFrame, aes( x = scale,
                                           y = ms,
                                           ymin = ms,
                                           ymax = ms + std ) )

# ------------------------------
# Fundamental Variables Assigned
# ------------------------------

print( "Generating fundamental graph data." )

defaultTextSize()

barWidth <- 0.9

xScaleConfig <- scale_x_continuous( breaks=c( 1, 3, 5, 7, 9 ) )

xLabel <- xlab( "Scale" )
yLabel <- ylab( "Latency (ms)" )
fillLabel <- labs( fill="Type" )

theme <- graphTheme()

title <- labs( title = chartTitle, subtitle = lastUpdatedLabel( latestBuildDate ) )

errorBarColor <- rgb( 140, 140, 140, maxColorValue = 255 )

fundamentalGraphData <- mainPlot +
                        xScaleConfig +
                        xLabel +
                        yLabel +
                        fillLabel +
                        theme +
                        title

# ---------------------------
# Generating Bar Graph Format
# ---------------------------

print( "Generating bar graph with error bars." )

barGraphFormat <- geom_bar( stat = "identity",
                            position = position_dodge(),
                            width = barWidth,
                            fill = webColor( "purple" ) )

errorBarFormat <- geom_errorbar( position = position_dodge(),
                                 width = barWidth,
                                 color = webColor( "darkerGray" ) )

values <- geom_text( aes( x=dataFrame$scale,
                          y=dataFrame$ms + 0.06 * max( dataFrame$ms ),
                          label = format( dataFrame$ms,
                                          digits=3,
                                          big.mark = ",",
                                          scientific = FALSE ) ),
                          size = 7.0,
                          fontface = "bold" )

result <- fundamentalGraphData +
          barGraphFormat +
          errorBarFormat +
          values

# -----------------------
# Exporting Graph to File
# -----------------------

saveGraph( errBarOutputFile )
