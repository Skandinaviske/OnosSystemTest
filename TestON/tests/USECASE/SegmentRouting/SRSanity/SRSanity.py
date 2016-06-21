# This test should always succeed. it runs cases 1,2,3
#CASE1: 2x2 Leaf-Spine topo and test IP connectivity
#CASE2: 4x4 topo + IP connectivity test
#CASE3: 2x2 topo + 3-node ONOS CLUSTER + IP connectivity test

class SRSanity:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        Sets up 1-node Onos-cluster
        Start 2x2 Leaf-Spine topology
        Pingall
        """
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as run
        if not hasattr(main,'apps'):
            run.initTest(main)

        description = "Bridging and Routing sanity test with 2x2 Leaf-spine "
        main.case( description )

        main.cfgName = '2x2'
        main.numCtrls = 1
        run.installOnos(main)
        run.startMininet(main, 'cord_fabric.py')
        #pre-configured routing and bridging test
        run.checkFlows(main, flowCount=116)
        run.pingAll(main, "CASE1")
        #TODO Dynamic config of hosts in subnet
        #TODO Dynamic config of host not in subnet
        #TODO Dynamic config of vlan xconnect
        #TODO Vrouter integration
        #TODO Mcast integration
        run.cleanup(main)

    def CASE2( self, main ):
        """
        Sets up 1-node Onos-cluster
        Start 4x4 Leaf-Spine topology
        Pingall
        """
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as run
        if not hasattr(main,'apps'):
            run.initTest(main)
        description = "Bridging and Routing sanity test with 4x4 Leaf-spine "
        main.case( description )
        main.cfgName = '4x4'
        main.numCtrls = 1
        run.installOnos(main)
        run.startMininet(main, 'cord_fabric.py', args="--leaf=4 --spine=4")
        #pre-configured routing and bridging test
        run.checkFlows(main, flowCount=350)
        run.pingAll(main, 'CASE2')
        #TODO Dynamic config of hosts in subnet
        #TODO Dynamic config of host not in subnet
        #TODO Dynamic config of vlan xconnect
        #TODO Vrouter integration
        #TODO Mcast integration
        run.cleanup(main)

    def CASE3( self, main ):
        """
        Sets up 3-node Onos-cluster
        Start 2x2 Leaf-Spine topology
        Pingall
        """
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as run
        if not hasattr(main,'apps'):
            run.initTest(main)
        description = "Bridging and Routing sanity test with 2x2 Leaf-spine "
        main.case( description )
        main.cfgName = '2x2'
        main.numCtrls = 3
        run.installOnos(main)
        run.startMininet(main, 'cord_fabric.py')
        #pre-configured routing and bridging test
        run.checkFlows(main, flowCount=116)
        run.pingAll(main, 'CASE3')
        #TODO Dynamic config of hosts in subnet
        #TODO Dynamic config of host not in subnet
        #TODO Dynamic config of vlan xconnect
        #TODO Vrouter integration
        #TODO Mcast integration
        run.cleanup(main)