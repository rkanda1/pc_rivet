# -- import modules
import pymel.core as pm
import maya.cmds as mc


# -- multi string replace
def multiReplace(str='', **kwargs):
    for k, v in kwargs.items():
        str = str.replace(k, v)
    return str


# -- add pc rivet attr
def addPcRivetVtxAttr(loc, vtx, lock=False):
    loc = pm.PyNode(loc)
    if not pm.objExists('{0}.pcRivet_vtx'.format(loc.name())):
        pm.addAttr(loc, ln='pcRivet_vtx', dt='string')
        loc.pcRivet_vtx.set(vtx)

    else:
        loc.pcRivet_vtx.set(vtx)

    if lock:
        loc.pcRivet_vtx.lock(True)


def pcRivetToVertex(vtx='', loc=''):
    # -- declare variables
    vtx = pm.Component(vtx)
    pos = pm.xform(vtx, ws=True, t=True, q=True)
    skn = pm.mel.eval('findRelatedSkinCluster {0};'.format(vtx.node().name()))
    rep = {'.':'_', '[':'_', ']':'_'}
    
    if skn:
        jtList = pm.skinCluster(skn, inf=True, q=True)
        wtList = pm.skinPercent(skn, vtx, v=True, q=True)

        # -- create dictionary joint and skin weight
        wtInfo = {}
        for i in range(len(jtList)):
            wtInfo.update({jtList[i]:wtList[i]})

        useInf = [inf for inf in wtInfo if wtInfo[inf] > 0.000]

        # -- create locator and set parent constrant
        if loc:
            loc = pm.PyNode(loc)
        else:
            loc = pm.spaceLocator(n='{0}pcRivet'.format(multiReplace(vtx.name(), **rep)))
        loc.t.set(pos)
        
        for inf in useInf:
            pm.parentConstraint(inf, loc, w=wtInfo[inf], mo=True)
        pc = pm.listRelatives(loc, typ='parentConstraint', c=True)
        
        # -- add pc rivet attr
        addPcRivetVtxAttr(loc, vtx.name(), False)
        
        return loc.name()

    else:
        pm.warning('Please select vertex which is a skin binded mesh.')
        return None


def rePcConstrain(loc):
    # -- declare variables
    loc = pm.PyNode(loc)
    vtx = loc.pcRivet_vtx.get()
    pcRivetToVertex(vtx, loc)
 