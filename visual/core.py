"""
Plots for classes, etc in pyfusion/core.py
"""
import pylab as pl, pyfusion
from matplotlib.widgets import CheckButtons
from numpy import arange, fft, resize, zeros, array
from types import FunctionType, StringTypes

class GenericPlot(object):
    def __init__(self,*args,**kwargs):
        """
        arg 0 is list of datapoints
        other non-keyword args are data mappings
        keyword args are passed to pylab
        """
        self.data = args[0]
        self.mappings = {}
	self.kwargs = kwargs
        for i,argi in enumerate(args[1:]):
            self.mappings[str(i)] = [datamap(self.data, argi_x) for argi_x in argi]
	self.setp()
    def setp(self):
        pl.setp(pl.gca(), **self.kwargs)



def datalookup(data, var_list, element_list):
    for i,vi in enumerate(var_list):
        data = data.__getattribute__(vi)
        if element_list[i] != None:
            data = data[element_list[i]]
    return data

def datamap(data, mapper):
    if type(mapper) == FunctionType:
        return datamap_func(data, mapper)
    elif type(mapper) in StringTypes:
        return datamap_str(data, mapper)
    else:
        raise TypeError, 'Unknown mapper type in datamap'

def datamap_func(data,mapper):
    return map(mapper, data)

def datamap_str(data, mapper):
    output = []
    dotstr = mapper.split('.')
    var_list = []
    element_list = []
    for dst in dotstr:
        if '[' in dst:
            dspl = dst.split('[')
            element_list.append(int(dspl[1][:-1]))
            var_list.append(dspl[0])
        else:
            var_list.append(dst)
            element_list.append(None)
    for dp in data:
        output.append(datalookup(dp,var_list, element_list))
    return output

class ScatterPlot(GenericPlot):
    def __init__(self,*args,**kwargs):
        super(ScatterPlot, self).__init__(*args,**kwargs)
        cols = 'brgky'
        for i in range(len(self.mappings['0'])):
            pl.plot(self.mappings['0'][i],self.mappings['1'][i],'%so' %cols[i])
	# seems some settings don't hold after plot, redo them
        super(ScatterPlot, self).setp()



def posNegFill(x,y1,y2):
	diff = y2 - y1
	pos = []
	neg = []
	xx1 = [x[0]]
	xx2 = [x[0]]
	yy1 = [y1[0]]
	yy2 = [y2[0]]
	oldSign = (diff[0] < 0 )
	npts = x.shape[0]
	for i in range(1,npts):
		newSign = (diff[i] < 0)
		if newSign != oldSign:
			xz,yz = findZero(i,x,y1,y2)
			xx1.append(xz)
			yy1.append(yz)
			xx2.reverse()
			xx1.extend(xx2)
			yy2.reverse()
			yy1.extend(yy2)
			if oldSign:
				neg.append( (xx1,yy1) )
			else:
				pos.append( (xx1,yy1) )
			xx1 = [xz,x[i]]
			xx2 = [xz,x[i]]
			yy1 = [yz,y1[i]]
			yy2 = [yz,y2[i]]
			oldSign = newSign
		else:
			xx1.append( x[i])
			xx2.append( x[i])
			yy1.append(y1[i])
			yy2.append(y2[i])
			if i == npts-1:
				xx2.reverse()
				xx1.extend(xx2)
				yy2.reverse()
				yy1.extend(yy2)
				if oldSign :
					neg.append( (xx1,yy1) )
				else:
					pos.append( (xx1,yy1) )
	return pos,neg

#used in topo plot
def findZero(i,x,y1,y2):
	im1 = i-1
	#print y1[i],y1[im1],x[i],x[im1],(x[i]-x[im1])
	m1 = (y1[i] - y1[im1])/(x[i] - x[im1])
	m2 = (y2[i] - y2[im1])/(x[i] - x[im1])
	b1 = y1[im1] - m1*x[im1]
	b2 = y2[im1] - m2*x[im1]
	xZero = (b1 - b2)/(m2 - m1)
	yZero = m1*xZero + b1
	return (xZero, yZero)

# used in topo plot
def join_ends(inarray,add_2pi = False,add_360deg=False,add_lenarray=False,add_one=False):
	output = resize(inarray,(len(inarray)+1,))
	if add_2pi:
		output[-1] = output[-1]+2*pi
	elif add_360deg:
		output[-1] = output[-1]+360.0
	elif add_lenarray:
		output[-1] = output[-1]+len(inarray)+1
	elif add_one:
		output[-1] = output[-2]+1
	return output



class Energy:
	def __init__(self,energy_list,initial_list):
		self.value = 0.0
		self.energy_list = energy_list
		for i in range(len(initial_list)):
			if initial_list[i]:
				self.value += self.energy_list[i]
	def add(self,elmt):
		self.value += self.energy_list[elmt]
	def sub(self,elmt):
		self.value -= self.energy_list[elmt]



def interactive_svd_plot(input_svd):
    """
    not finished yet - just imported some old code and made useable...
    """
    sv_query = pyfusion.session.query(pyfusion.SingularValue).filter_by(svd = input_svd).order_by(pyfusion.SingularValue.number)

    sv_list = [i for i in sv_query]
    n_SV = len(sv_list)
    # define axes 
    ax1 = pl.subplot(221)
    ax2 = pl.subplot(222)
    ax3 = pl.subplot(223)
    ax4 = pl.subplot(224)

    # allow space for check buttons
    pl.subplots_adjust(left=0.2)

    # setup check boxes
    rax = pl.axes([0.01, 0.05, 0.09, 0.9])

    # CheckButtons take tuple arguments, tuples are immutable, so create lists fom svd info, and then cast as tuple
    button_name_list=[]
    button_setting_list=[]

    for i in range(n_SV):
	button_name_list.append('  '+str(i))
	button_setting_list.append(False)
        
    # have first 2 SVs on as default
    for i in [0,1]:
	button_setting_list[i] = True

    check = CheckButtons(rax, tuple(button_name_list), tuple(button_setting_list))
    # hack to make check buttons square
    check_box_stretch = 7
    for i in range(len(check.rectangles)):
	check.rectangles[i].set_width(check_box_stretch*check.rectangles[i].get_height())
	for j in [0,1]: # two lines of the x
            orig_x_data = check.lines[i][j].get_xdata()
            orig_y_data = check.lines[i][j].get_ydata()
            orig_width = orig_x_data[1]-orig_x_data[0]
            new_width = check_box_stretch*orig_width
            new_x_data = [orig_x_data[0],orig_x_data[0]+new_width]
            check.lines[i][j].set_data(new_x_data,orig_y_data)

    # plot all SVs, use button_setting_list for initial visibility
    # axes 1: chrono
    pl.axes(ax1)
    pl.xlabel('Time [ms]')
    pl.ylabel('Amplitude [a.u.]')
    plot_list_1 = range(n_SV)
    for sv_i, sv in enumerate(sv_list):
	plot_list_1[sv_i], = ax1.plot(1.e3*array(input_svd.timebase), sv.chrono, visible= button_setting_list[sv_i],alpha=0.5)
    pl.xlim(1.e3*min(input_svd.timebase), 1.e3*max(input_svd.timebase))

    # axes 2: SVs
    plot_list_2 = range(n_SV)
    pl.axes(ax2)
    sv_sv = [i.value for i in sv_list]
    ax2.semilogy(arange(n_SV),sv_sv,'ko',markersize=3)
    entropy = input_svd.entropy
    pl.xlabel('Singular Value number')
    pl.ylabel('Singular Value')
    pl.figtext(0.75,0.83,'1/H = %.2f' %(1./entropy),fontsize=12, color='r')
    pl.figtext(0.75,0.81,'H = %.2f' %(entropy),fontsize=12, color='b')
    energy_list = [i*i/input_svd.energy for i in sv_sv]
    energy = Energy(energy_list,button_setting_list)
    # this is done in two places - potential for inconsistency - wish I knew better
    energy_label = pl.figtext(0.75,0.78,'E = %.2f %%' %(100.*energy.value),fontsize=12, color='b')
    # grid('True')
    for sv_i, sv in enumerate(sv_list):
	col = plot_list_1[sv_i].get_color()
	plot_list_2[sv_i], = ax2.semilogy([sv_i], [sv.value], '%so' %(col),visible= button_setting_list[sv_i],markersize=8,alpha=0.5)

    # axes 3: fft(chrono)
    pl.axes(ax3)
    plot_list_3 = range(n_SV)
    pl.xlabel('Frequency [kHz]')
    pl.ylabel('Power Spectrum')
    pl.grid('True')
    nyquist_kHz = 1.e-3*0.5/(input_svd.timebase[1]-input_svd.timebase[0])
    for sv_i,sv in enumerate(sv_list):
        col = plot_list_1[sv_i].get_color()
        tmp_chrono = sv.chrono
        tmp_fft = fft.fft(tmp_chrono)[:len(tmp_chrono)/2]
        freq_array = nyquist_kHz*arange(len(tmp_fft))/(len(tmp_fft)-1)
        plot_list_3[sv_i], = ax3.plot(freq_array, abs(tmp_fft), col,visible= button_setting_list[sv_i],alpha=0.5)
        
    pl.xlim(0,nyquist_kHz)

    # axes 4: topo
    pl.axes(ax4)
    plot_list_4 = range(n_SV)
    pl.xlabel('Channel')
    pl.ylabel('Topo [a.u.]')
    angle_array = arange(n_SV+1)
    channel_names = input_svd.timesegment.data[input_svd.diagnostic.name].ordered_channel_list
    channel_names.append(channel_names[0])
    pl.xticks(angle_array,channel_names, rotation=90)
    for sv_i,sv in enumerate(sv_list):
	col = plot_list_1[sv_i].get_color()
	tmp_topo = join_ends(sv.topo)
	pos,neg =  posNegFill(angle_array,zeros(len(angle_array)),tmp_topo)
	### BUG: it looks like ax4.fill doesn't work in a couple of cases, leaving sub_plot_4_list[i] as int, which raises a set_visible() bug in button_action - also has problems with draw(). other subplots all worked fine before I started with subplot 4
	sub_plot_4_list = range(len(pos)+len(neg)+2)
	for j in range(len(pos)):
            sub_plot_4_list[j], = ax4.fill(pos[j][0],pos[j][1],col,visible= button_setting_list[sv_i],alpha=0.5)
        for j in range(len(neg)):
            sub_plot_4_list[j+len(pos)], = ax4.fill(neg[j][0],neg[j][1],col,visible= button_setting_list[sv_i],alpha=0.5)
		
	sub_plot_4_list[len(neg)+len(pos)+0], = ax4.plot(angle_array,tmp_topo,'%so' %(col),visible= button_setting_list[sv_i],markersize=3)
	# show repeated val
	sub_plot_4_list[len(neg)+len(pos)+1], = ax4.plot([angle_array[-1]],[tmp_topo[-1]],'kx', visible= button_setting_list[sv_i],markersize=6)
	plot_list_4[sv_i]=sub_plot_4_list

    def button_action(label):
	# this is not very clear: but basically, the label is the str() of the element of plot_list_x we want to make / unmake visible
	visible_status = plot_list_1[int(label)].get_visible()
	plot_list_1[int(label)].set_visible(not visible_status)
	plot_list_2[int(label)].set_visible(not visible_status)
	plot_list_3[int(label)].set_visible(not visible_status)
	for i in range(len(plot_list_4[int(label)])):
            plot_list_4[int(label)][i].set_visible(not visible_status)
	# if visible_status == False, then we are adding visiblity => add to energy, vice-verca
	if visible_status:
            energy.sub(int(label))
	else:
            energy.add(int(label))
	energy_label._text='E = %.2f %%' %(100.*energy.value)
	pl.draw()

    # action when button is clicked
    check.on_clicked(button_action)

    # show plot
    pl.show()
    
