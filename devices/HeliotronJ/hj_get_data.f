c *** program for loading data of mp fast samping            ***
c *** connection to IDL                                      *** 
c *** In the IDLprogram, you have to use "spawn, 'load_pmp'" ***
c *** programed by S. Yamamoto on Feb. 14, 2005              ***
c *** hacked by D. Pretty on Feb.  2008                      ***
c
      subroutine gethjdata (ishotno,lendata,chname,outname)
       implicit real (a-h,o-z)
cf2py intent(callback) getdata
       external getdata
       integer nch,lendata
       character*100 outname
       character*100 chname
c
c *** define array and parameter ***
c      dimension dataary(nch,lendata),
       dimension tary(lendata)
c     dimension tary(262144)
       dimension tmpary(lendata)
       integer iadc_bit,iampfilt,ishotno
       integer ibhv,ibta,ibtb,ibav,ibiv
       integer ich,isample,iswch
       integer ierror
c       character*16 signalnm(nch),modulenm
      character*16 signalnm,modulenm
      character*100 paneldt
      character*21 datascl,dataunit
      character*6 stime
      character*9 sdate
c
c *** define signal name ***
C      signalnm(1) ='PMP1'
c      signalnm(2) ='PMP2'
c      signalnm(3) ='PMP3'
c      signalnm(4) ='PMP4'
c      signalnm(5) ='PMP5'
c      signalnm(6) ='PMP6'
c      signalnm(7) ='PMP7'
c      signalnm(8) ='PMP8'
c      signalnm(9) ='PMP9'
c      signalnm(10)='PMP10'
c      signalnm(11)='PMP11'
c      signalnm(12)='PMP12'
c      signalnm(13)='PMP13'
c      signalnm(14)='PMP14'
c
c *** read shot number from text ***
c      open(20, file='tmp_sn.dat') 
c      read(20, *) ishotno
c      close(20) 
      iswch=1
c
c *** load data ***
c      do 100 i=1,14
      call getdata(chname,modulenm,paneldt,datascl,dataunit,sdate,
     &  stime,tmpary,tary,tsamp,tdelay,ampgain,sc_max,sc_min,bitzero,
     &  iadc_bit,iampfile,ishotno,ibhv,ibta,ibtb,ibav,ibiv,
     &  ich,isample,iswch,ierror)
c        do 200 j=1,262144
c            dataary(i,j) = tmpary(j)
c  200   continue
c  100 continue
c
c *** check error ***
      if(ierror.ne.0) write(6,*) 'MP data NOT found'
      if(ierror.eq.0) write(6,*) 'MP data found'
c
c *** write data ***
      open(21, file=outname)
      do 300 jt=1,lendata
          write(21,*), tary(jt), tmpary(jt)
 300   continue
      close(21)
c      common /data/ iswch
c      print*, "iswch=",iswch
c
c *** stop program ***
      end
c
